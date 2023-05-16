import logging
from uuid import UUID
from typing import List

from elasticsearch.exceptions import NotFoundError

from core.messages import FILM_NOT_FOUND_ES
from .base import BaseElasticStorage
from db.models.elastic_models import SerializedFilm, SerializedGenre
from models.film import ShortFilm, DetailFilm


class FilmElasticRepository(BaseElasticStorage):
    async def get_by_id(self, film_uuid: UUID) -> DetailFilm:
        doc = await self._get_by_id('movies', film_uuid, None)
        if doc is None:
            logging.error(FILM_NOT_FOUND_ES, 'id', film_uuid)
            return None
        genres = []
        for genre_name in doc['_source']['genre']:
            q = {'query': {'match_phrase': {'name': genre_name}}}
            res = await self._search(
                index='genres', body_of_query=q
            )
            genre_id = res[0]['_source']['id']
            genres.append({'id': genre_id, 'name': genre_name})
        doc['_source']['genre'] = genres
        ser_film = SerializedFilm(**doc['_source'])
        film = DetailFilm.from_serialized_movie(ser_film)
        return film

    async def get_by_title(
            self,
            film_title: str,
            page_size: int,
            page_number: int
    ) -> List[ShortFilm] | None:
        body_of_q = {"query": {"match": {"title": {"query": film_title, "fuzziness": "AUTO"}}}}
        doc = await self._search('movies', body_of_q, page_number, page_size)
        if doc is None:
            logging.error(FILM_NOT_FOUND_ES, 'query', film_title)
            return None
        films = list(map(
            lambda fl: ShortFilm(
                uuid=fl['_source']['id'],
                title=fl['_source']['title'],
                imdb_rating=fl['_source']['imdb_rating']
            ),
            doc,
        ))
        return films

    async def get_by_sort(
            self,
            sort: str,
            page_size: int,
            page_number: int,
            genre_id: UUID | None
    ) -> list[ShortFilm] | None:

        if sort.startswith('-'):
            type_sort = 'desc'
            sort_value = sort[1:]
        else:
            type_sort = 'asc'
            sort_value = sort

        if genre_id:
            genre_inf: SerializedGenre = await self._get_by_id(
                'genres', genre_id, SerializedGenre
            )
            q = {'match': {'genre': genre_inf.name}}
        else:
            q = {"match_all": {}}
        doc = await self._search(
            index='movies',
            body_of_query={'query': q, 'sort': [{sort_value: type_sort}]},
            size=page_size,
            page_number=page_number
        )
        if doc is None:
            logging.error(FILM_NOT_FOUND_ES, 'sort', sort)
            return None

        films = list(map(
            lambda fl: ShortFilm(
                uuid=fl['_source']['id'],
                title=fl['_source']['title'],
                imdb_rating=fl['_source']['imdb_rating']
            ),
            doc,
        ))
        return films


film_repository: FilmElasticRepository | None = None


def get_film_repository() -> FilmElasticRepository:
    return film_repository
