import logging
from functools import lru_cache
from uuid import UUID

import orjson
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from core.messages import (
    TOTAL_GENRES_NOT_FOUND,
    GENRE_NOT_FOUND,
    GENRE_CACHE_NOT_FOUND,
    TOTAL_GENRE_CACHE_NOT_FOUND
)
from db.elastic import get_elastic
from db.models.elastic_models import SerializedGenre
from db.redis import get_redis
from models.genre import Genre
from services.redis_utils import key_generate

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_all(self) -> list[Genre]:
        genres = await self._genres_from_cache()
        if not genres:
            ser_genre = await self._get_genres_from_elastic()
            genres = [Genre.from_serialized_genre(s_g) for s_g in ser_genre]
            if not genres:
                logging.info(TOTAL_GENRES_NOT_FOUND)
                return None
            await self._put_genres_to_cache(genres)
        return genres

    async def get_by_id(self, genre_id: UUID) -> Genre | None:
        genre = await self._genre_from_cache(genre_id)
        if not genre:
            ser_genre = await self._get_genre_from_elastic(genre_id)
            if not ser_genre:
                logging.info(GENRE_NOT_FOUND, 'genre_id', genre_id)
                return None
            genre = Genre.from_serialized_genre(ser_genre)
            await self._put_genre_to_cache(genre)
        return genre

    async def _get_genres_from_elastic(self) -> list[SerializedGenre]:
        q = {'match_all': {}}
        _doc = await self.elastic.search(index='genres', body={'query': q})
        all_genres = [
            SerializedGenre(**g['_source'])
            for g in _doc['hits']['hits']
        ]
        return all_genres

    async def _genre_from_cache(self, genre_id: UUID) -> Genre | None:
        key = await key_generate(genre_id)
        data = await self.redis.get(key)
        if not data:
            logging.info(GENRE_CACHE_NOT_FOUND, 'genre_id', genre_id)
            return None
        genre = Genre.parse_raw(data)
        return genre

    async def _genres_from_cache(self) -> list[Genre] | None:
        key = await key_generate(source='all_genres')
        data = await self.redis.get(key)
        if not data:
            logging.error(TOTAL_GENRE_CACHE_NOT_FOUND)
            return None
        return [Genre.parse_raw(item) for item in orjson.loads(data)]

    async def _put_genres_to_cache(self, genres: list[Genre]) -> None:
        key = await key_generate(source='all_genres')
        await self.redis.set(
            key,
            orjson.dumps([genre.json(by_alias=True) for genre in genres]),
            GENRE_CACHE_EXPIRE_IN_SECONDS
        )

    async def _put_genre_to_cache(self, genre: Genre) -> None:
        key = await key_generate(genre.uuid)
        await self.redis.set(key, genre.json(),
                             GENRE_CACHE_EXPIRE_IN_SECONDS)

    async def _get_genre_from_elastic(
            self, genre_id: UUID
    ) -> SerializedGenre | None:
        try:
            doc = await self.elastic.get('genres', genre_id)
        except NotFoundError:
            logging.error(GENRE_CACHE_NOT_FOUND, 'genre_id', genre_id)
            return None
        return SerializedGenre(**doc['_source'])


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
