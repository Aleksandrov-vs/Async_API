from uuid import UUID
from typing import List

from .base import BaseElasticStorage
from db.models.elastic_models import SerializedGenre
from models.genre import Genre


class GenreElasticRepository(BaseElasticStorage):
    async def get_by_id(self, genre_id: UUID) -> Genre | None:
        ser_genre = await self._get_by_id(
            'genres',
            genre_id,
            SerializedGenre
        )
        if ser_genre is None:
            return None
        return Genre.from_serialized_genre(ser_genre)

    async def get_all_genres(self) -> List[Genre] | None:
        body_of_q = {'query': {'match_all': {}}}
        _doc = await self._search(
            index='genres',
            body_of_query=body_of_q
        )
        all_ser_genres = [
            SerializedGenre(**g['_source'])
            for g in _doc
        ]
        all_genre = [
            Genre.from_serialized_genre(g)
            for g in all_ser_genres
        ]

        return all_genre


genre_repository: GenreElasticRepository | None = None


def get_genre_repository() -> GenreElasticRepository:
    return genre_repository
