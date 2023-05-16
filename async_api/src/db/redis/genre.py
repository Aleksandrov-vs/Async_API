import logging
from uuid import UUID

from orjson import orjson

from core.messages import GENRE_CACHE_NOT_FOUND, TOTAL_GENRE_CACHE_NOT_FOUND
from db.redis.base import RedisStorage
from models.genre import Genre


class GenreCacheRepository(RedisStorage):
    async def get_by_id(self, genre_id: UUID) -> Genre | None:
        key = self._key_generate(genre_id)
        data = await self.redis.get(key)
        if not data:
            logging.info(GENRE_CACHE_NOT_FOUND, 'genre_id', genre_id)
            return None
        genre = Genre.parse_raw(data)
        return genre

    async def get_all(self) -> list[Genre] | None:
        key = self._key_generate(source='all_genres')
        data = await self.redis.get(key)
        if not data:
            logging.error(TOTAL_GENRE_CACHE_NOT_FOUND)
            return None
        return [Genre.parse_raw(item) for item in orjson.loads(data)]

    async def put_genres(self, genres: list[Genre]) -> None:
        key = self._key_generate(source='all_genres')
        await self.redis.set(
            key,
            orjson.dumps([genre.json(by_alias=True) for genre in genres])
        )

    async def put_genre(self, genre: Genre) -> None:
        key = self._key_generate(genre.uuid)
        await self.redis.set(key, genre.json())


genre_cache_repository: GenreCacheRepository | None = None


def get_genre_cache_repository() -> GenreCacheRepository:
    return genre_cache_repository
