import logging
from functools import lru_cache
from typing import List, Optional
from uuid import UUID

import orjson
from db.elastic import get_elastic
from db.models.elastic_models import SerializedGenre
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.genre import Genre
from redis.asyncio import Redis
from services.redis_utils import key_generate

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5


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
                logging.info('Genres is not found!')
                return None
            await self._put_genres_to_cache(genres)
        return genres

    async def get_by_id(self, genre_id: UUID) -> Optional[Genre]:
        genre = await self._genre_from_cache(genre_id)
        if not genre:
            ser_genre = await self._get_genre_from_elastic(genre_id)
            if not ser_genre:
                logging.info('Genres is not found!')
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

    async def _genre_from_cache(self, genre_id: UUID) -> Optional[Genre]:
        key = await key_generate(genre_id)
        data = await self.redis.get(key)
        if not data:
            logging.error(f'Cache is empty...')
            return None
        genre = Genre.parse_raw(data)
        return genre

    async def _genres_from_cache(self) -> Optional[List[Genre]]:
        key = await key_generate(source='all_genres')
        data = await self.redis.get(key)
        if not data:
            logging.error(f'Cache is empty...')
            return None
        return [Genre.parse_raw(item) for item in orjson.loads(data)]

    async def _put_genres_to_cache(self, genres: List[Genre]) -> None:
        key = await key_generate(source='all_genres')
        await self.redis.set(key, orjson.dumps([genre.json(by_alias=True) for genre in genres]),
                             GENRE_CACHE_EXPIRE_IN_SECONDS)

    async def _put_genre_to_cache(self, genre: Genre) -> None:
        key = await key_generate(genre.uuid)
        await self.redis.set(key, genre.json(),
                             GENRE_CACHE_EXPIRE_IN_SECONDS)

    async def _get_genre_from_elastic(
            self, genre_id: UUID
    ) -> Optional[SerializedGenre]:
        try:
            doc = await self.elastic.get('genres', genre_id)
        except NotFoundError:
            logging.error(f'Elastic not found error!')
            return None
        return SerializedGenre(**doc['_source'])


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
