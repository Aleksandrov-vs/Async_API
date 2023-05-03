from functools import lru_cache
from typing import List, Optional
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.models.elastic_models import SerializedGenre
from db.redis import get_redis
from models.genre import Genre


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_all(self) -> Optional[List[Genre]]:
        genres = await self._genres_from_cache()
        if not genres:
            ser_genre = await self._get_genres_from_elastic()
            genres = [Genre.from_serialized_genre(s_g) for s_g in ser_genre]
            if not genres:
                return None
            for genre in genres:
                await self._put_genre_to_cache(genre)

        return genres

    async def get_by_id(self, genre_id: UUID) -> Optional[Genre]:
        genre = await self._genre_from_cache()
        if not genre:
            ser_genre = await self._get_genre_from_elastic(genre_id)
            if not ser_genre:
                return None
            genre = Genre.from_serialized_genre(ser_genre)
            await self._put_genre_to_cache(genre)
        return genre

    async def _get_genres_from_elastic(self) -> List[SerializedGenre]:
        q = {'match_all': {}}
        _doc = await self.elastic.search(index='genres', body={'query': q})
        all_genres = [
            SerializedGenre(**g['_source'])
            for g in _doc['hits']['hits']
        ]
        return all_genres

    async def _genres_from_cache(self):
        return None

    async def _put_genre_to_cache(self, genre):
        return None

    async def _genre_from_cache(self):
        return None

    async def _get_genre_from_elastic(
            self, genre_id: UUID
    ) -> Optional[SerializedGenre]:
        try:
            doc = await self.elastic.get('genres', genre_id)
        except NotFoundError:
            return None
        return SerializedGenre(**doc['_source'])


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
