import logging
from functools import lru_cache
from uuid import UUID

import orjson
from fastapi import Depends
from elasticsearch import NotFoundError

from src.db.base import RedisBaseStorage, ElasticBaseStorage
from src.services.base_serivce import BaseService
from core.messages import (
    FILM_NOT_FOUND,
    FILM_NOT_FOUND_ES,
    FILM_CACHE_NOT_FOUND
)
from Async_API_sprint_1.async_api.src.db.elastic_storage import get_elastic
from db.models import elastic_models
from Async_API_sprint_1.async_api.src.db.redis_storage import get_redis
from models.film import DetailFilm, ShortFilm
from services.redis_utils import key_generate

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService(BaseService):
    def __init__(self, redis_storage: RedisBaseStorage, es_storage: ElasticBaseStorage):
        super().__init__(redis_storage, es_storage)

    async def get_by_id(self, film_id: str) -> DetailFilm | None:
        film = await self.get_data_from_redis(name_id='film_id',
                                              uuid=film_id,
                                              model=DetailFilm)
        if not film:
            film = await self.get_data_from_elastic(index='movies',
                                                    uuid=film_id,
                                                    model=DetailFilm)
            if not film:
                logging.info(FILM_NOT_FOUND, 'id', film_id)
                return None
            await self.put_data_to_redis(name_id='film_id',
                                         data=film)
        return film

    async def get_by_sort(self,
                          sort: str,
                          page_size: int,
                          page_number: int,
                          genre: UUID | None
    ) -> list[ShortFilm] | None:
        films = await self._film_by_sort_from_cache(
            sort, page_size,
            page_number, genre
        )
        if not films:
            films = await self._get_films_by_sort_from_elastic(sort,
                                                               page_size,
                                                               page_number,
                                                               genre)
            if not films:
                logging.info(FILM_NOT_FOUND, 'sort', sort)
                return None
            await self._put_sort_films_to_cache(films, sort, page_size, page_number, genre)
        return films

    async def get_by_query(self, query: str, page_size: int,
                           page_number: int) -> list[ShortFilm] | None:
        films = await self._get_films_by_query_from_elastic(
            query, page_size,
            page_number
        )
        if not films:
            logging.info(FILM_NOT_FOUND, 'query', query)
            return None
        return films

    async def _get_films_by_query_from_elastic(
            self, query: str,
            page_size: int, page_number: int) -> list[ShortFilm] | None:
        q = {"match": {"title": {"query": query, "fuzziness": "AUTO"}}}
        try:
            doc = await self.elastic.search(
                index='movies',
                body={
                    "query": q
                },
                from_=page_size * (page_number - 1),
                size=page_size
            )
        except NotFoundError:
            logging.error(FILM_NOT_FOUND_ES, 'query', query)
            return None
        films = list(map(
            lambda fl: ShortFilm(
                uuid=fl['_source']['id'],
                title=fl['_source']['title'],
                imdb_rating=fl['_source']['imdb_rating']
            ),
            doc['hits']['hits'],
        ))
        return films

    async def _get_film_from_elastic(self, film_id: str) \
            -> DetailFilm | None:
        try:
            doc = await self.elastic.get('movies', film_id)
        except NotFoundError:
            logging.error(FILM_NOT_FOUND_ES, 'id', film_id)
            return None
        genres = []
        for genre_name in doc['_source']['genre']:
            q = {'query': {'match_phrase': {'name': genre_name}}}
            res = await self.elastic.search(
                index='genres', body=q
            )
            genre_id = res['hits']['hits'][0]['_source']['id']
            genres.append({'id': genre_id, 'name': genre_name})
        doc['_source']['genre'] = genres
        ser_film = elastic_models.SerializedFilm(**doc['_source'])
        film = DetailFilm.from_serialized_movie(ser_film)
        return film

    async def _get_films_by_sort_from_elastic(self, sort: str, page_size: int, page_number: int,
                                              genre_id: UUID | None) -> list[ShortFilm] | None:
        if sort.startswith('-'):
            type_sort = 'desc'
            sort_value = sort[1:]
        else:
            type_sort = 'asc'
            sort_value = sort
        try:
            if genre_id:
                genre_inf = await self.elastic.get('genres', genre_id)
                genre_name = genre_inf['_source']['name']
                q = {'match': {'genre': genre_name}}
            else:
                q = {"match_all": {}}
            doc = await self.elastic.search(
                index='movies',
                body={'query': q, 'sort': [{sort_value: type_sort}]},
                from_=page_size * (page_number - 1),
                size=page_size
            )
        except NotFoundError:
            logging.error(FILM_NOT_FOUND_ES, 'sort', sort)
            return None
        films = list(map(
            lambda fl: ShortFilm(
                uuid=fl['_source']['id'],
                title=fl['_source']['title'],
                imdb_rating=fl['_source']['imdb_rating']
            ),
            doc['hits']['hits'],
        ))
        return films

    async def _film_from_cache(self, film_id: str) -> DetailFilm | None:
        key = await key_generate(film_id)
        data = await self.redis.get(key)
        if not data:
            logging.info(FILM_CACHE_NOT_FOUND, 'film_id', film_id)
            return None
        film = DetailFilm.parse_raw(data)
        return film

    async def _film_by_sort_from_cache(self, sort: str, page_size: int,
                                       page_number: int, genre: UUID | None):
        key = await key_generate(sort, page_size, page_number, genre)
        data = await self.redis.get(key)
        if not data:
            logging.info(FILM_CACHE_NOT_FOUND, 'sort', sort)
            return None
        return [ShortFilm.parse_raw(item) for item in orjson.loads(data)]

    async def _put_sort_films_to_cache(self, films: list[ShortFilm], sort: str, page_size: int,
                                       page_number: int, genre: UUID | None) -> None:
        key = await key_generate(sort, page_size, page_number, genre)
        await self.redis.set(key, orjson.dumps([film.json(by_alias=True) for film in films]),
                             FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
        redis: RedisBaseStorage = Depends(get_redis),
        elastic: ElasticBaseStorage = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
