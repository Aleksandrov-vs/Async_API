import logging
from uuid import UUID

from orjson import orjson
from pydantic import BaseModel

from core.messages import FILM_CACHE_NOT_FOUND
from db.redis.base import RedisStorage
from models.film import DetailFilm, ShortFilm


class FilmCacheRepository(RedisStorage):
    async def get_by_id(self, film_id: UUID) -> DetailFilm | None:
        key = self._key_generate(film_id)
        data = await self.redis.get(key)
        if not data:
            logging.info(FILM_CACHE_NOT_FOUND, 'film_id', film_id)
            return None
        film = DetailFilm.parse_raw(data)
        return film

    async def get_by_sort(self, sort: str, page_size: int,
                          page_number: int, genre: UUID | None):
        key = self._key_generate(sort, page_size, page_number, genre)
        data = await self.redis.get(key)
        if not data:
            logging.info(FILM_CACHE_NOT_FOUND, 'sort', sort)
            return None
        return [ShortFilm.parse_raw(item) for item in orjson.loads(data)]

    async def put_to_cache(self,
                           name_id: str,
                           data: BaseModel):
        await self.redis.set(
            f'{name_id}:{data.uuid}',
            data.json()
        )

    async def put_sort_films_to_cache(self, films: list[ShortFilm], sort: str, page_size: int,
                                      page_number: int, genre: UUID | None) -> None:
        key = self._key_generate(sort, page_size, page_number, genre)
        await self.redis.set(
            key,
            orjson.dumps([film.json(by_alias=True) for film in films]),
        )


film_cache_repository: FilmCacheRepository | None = None


def get_film_cache_repository() -> FilmCacheRepository:
    return film_cache_repository
