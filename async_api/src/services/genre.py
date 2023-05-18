import logging
from functools import lru_cache
from uuid import UUID
from typing import Protocol

from fastapi import Depends

from db.elastic.genre import get_genre_repository
from core.messages import (
    TOTAL_GENRES_NOT_FOUND,
    GENRE_NOT_FOUND,
)
from db.redis.genre import get_genre_cache_repository
from models.genre import Genre


class GenreCacheRepositoryProtocol(Protocol):
    async def get_by_id(self, genre_id: UUID) -> Genre | None:
        """возвращает описание жанра  из кеш по id"""
        ...

    async def get_all(self) -> list[Genre] | None:
        """возвращает список всех жанров"""
        ...

    async def put_genres(self, genres: list[Genre]) -> None:
        """добавить в кеш список жанров"""
        ...

    async def put_genre(self, genre: Genre) -> None:
        """добавить в кеш жанр"""
        ...


class GenreRepositoryProtocol(Protocol):
    async def get_by_id(self, genre_id: UUID) -> Genre | None:
        """возврашает описание жанра по Id"""
        ...

    async def get_all_genres(self) -> list[Genre] | None:
        """возвращает все жанры"""
        ...


class GenreService:
    def __init__(
            self,
            genre_cache_repository: GenreCacheRepositoryProtocol,
            genre_repository: GenreRepositoryProtocol):
        self._genre_cache_repository = genre_cache_repository
        self._genre_repository = genre_repository

    async def get_all(self) -> list[Genre] | None:
        genres = await self._genre_cache_repository.get_all()
        if not genres:
            genres = await self._genre_repository.get_all_genres()
            if not genres:
                logging.info(TOTAL_GENRES_NOT_FOUND)
                return None
            await self._genre_cache_repository.put_genres(genres)
        return genres

    async def get_by_id(self, genre_id: UUID) -> Genre | None:
        genre = await self._genre_cache_repository.get_by_id(genre_id=genre_id)
        if not genre:
            genre = await self._genre_repository.get_by_id(genre_id=genre_id)
            if not genre:
                logging.info(GENRE_NOT_FOUND, 'genre_id', genre_id)
                return None
            await self._genre_cache_repository.put_genre(genre)
        return genre


@lru_cache()
def get_genre_service(
        genre_cache_repository: GenreCacheRepositoryProtocol = Depends(get_genre_cache_repository),
        genre_repository: GenreRepositoryProtocol = Depends(get_genre_repository)
) -> GenreService:
    return GenreService(genre_cache_repository, genre_repository)
