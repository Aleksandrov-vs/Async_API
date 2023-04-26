import logging
from functools import lru_cache
from pprint import pprint
from typing import Optional, List
from uuid import UUID

from db.elastic import get_elastic
from db.redis import get_redis
from db.models import elastic_models
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.film import DetailFilm, ShortFilm
from redis.asyncio import Redis

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    # get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_id(self, film_id: str) -> Optional[DetailFilm]:
        film = await self._film_from_cache(film_id)
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def get_by_sort(self, sort: str, page_size: int,
                          page_number: int, genre: UUID | None):
        films = await self._film_by_sort_from_cache(sort, page_size,
                                                    page_number, genre)
        if not films:
            films = await self._get_films_by_sort_from_elastic(sort, page_size,
                                                               page_number, genre)
            if not films:
                return None
            await self._put_sort_films_to_cache(sort, page_size,
                                                page_number,
                                                genre)
            return films

    async def get_by_query(self, query, page_size, page_number):
        films = await self._film_by_query_from_cache(query, page_size,
                                                     page_number)
        if not films:
            films = await self._get_films_by_query_from_elastic(query, page_size,
                                                                page_number)
            if not films:
                return None
            await self._put_query_films_to_cache(query, page_size,
                                                 page_number)
            return films

    async def _get_films_by_query_from_elastic(self, query: str, page_size: int,
                                               page_number: int) -> Optional[List[ShortFilm]]:
        try:
            doc = await self.elastic.search(
                index='movies',
                body={

                    "query": {
                        "match": {
                            "title": {
                                "query": query,
                                "fuzziness": "AUTO"
                            }
                        }
                    }
                },
                from_=page_size * (page_number - 1),
                size=page_size
            )
        except NotFoundError:
            return None
        pprint(doc['hits']['hits'])
        films = list(map(
            lambda fl: ShortFilm(
                uuid=fl['_source']['id'],
                title=fl['_source']['title'],
                imdb_rating=fl['_source']['imdb_rating']
            ),
            doc['hits']['hits'],
        ))
        return films

    async def _get_film_from_elastic(self, film_id: str) -> Optional[DetailFilm]:
        try:
            doc = await self.elastic.get('movies', film_id)
        except NotFoundError:
            return None
        ser_film = elastic_models.SerializedFilm(**doc['_source'])
        film = DetailFilm.from_serialized_movie(ser_film)
        return film

    async def _get_films_by_sort_from_elastic(self, sort: str, page_size: int,
                                              page_number: int, genre: UUID | None) -> Optional[List[ShortFilm]]:
        if sort.startswith('-'):
            type_sort = 'desc'
            sort_value = sort[1:]
        else:
            type_sort = 'asc'
            sort_value = sort

        try:
            doc = await self.elastic.search(
                index='movies',
                body={
                    'query': {
                        'match_all': {}
                    },
                    'sort': [{sort_value: type_sort}]
                },
                from_=page_size * (page_number - 1),
                size=page_size
            )
        except NotFoundError:
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

    async def _film_from_cache(self, film_id: str) -> Optional[DetailFilm]:
        # data = await self.redis.get(film_id)
        # if not data:
        #     return None
        # film = Film.parse_raw(data)
        # return film
        return None

    async def _put_film_to_cache(self, film: DetailFilm):
        # await self.redis.set(film.id, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS)
        return None

    async def _film_by_sort_from_cache(self, sort, page_size, page_number, genre):
        return None

    async def _put_sort_films_to_cache(self, sort, page_size, page_number, genre):
        return None

    async def _film_by_query_from_cache(self, query, page_size, page_number):
        return None

    async def _put_query_films_to_cache(self, query, page_size, page_number):
        return None


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
