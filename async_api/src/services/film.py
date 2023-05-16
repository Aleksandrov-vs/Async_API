import logging
from functools import lru_cache
from uuid import UUID
from typing import Protocol

from fastapi import Depends
from pydantic import BaseModel

from core.messages import (
    FILM_NOT_FOUND,
)
from db.elastic.film import get_film_repository
from db.redis.film import get_film_cache_repository
from models.film import DetailFilm, ShortFilm


class FilmRepositoryProtocol(Protocol):
    async def get_by_id(self, film_uuid: UUID) -> DetailFilm | None:
        """возвращает подробное описание фильма по id"""
        ...

    async def get_by_title(
            self,
            film_title: str,
            page_size: int,
            page_number: int
    ) -> list[ShortFilm] | None:
        """возвращает список фильмов с похожим названием"""
        ...

    async def get_by_sort(
            self,
            sort: str,
            page_size: int,
            page_number: int,
            genre_id: UUID | None
    ) -> list[ShortFilm] | None:
        """возвращает фильмы с учетом сортировки и пагинации"""
        ...


class FilmCacheRepositoryProtocol:
    async def get_by_id(self, film_id: UUID) -> DetailFilm | None:
        """возвращает описание фильма по id из кеша"""
        ...

    async def get_by_sort(
            self, sort: str,
            page_size: int, page_number: int,
            genre: UUID | None
    ) -> list[ShortFilm] | None:
        """возвращает список коротких описаний фильмов с учетом сортировки из кеша"""
        ...

    async def put_to_cache(self, name_id: str, data: BaseModel) -> None:
        """добавить фильм в кеш"""
        ...

    async def put_sort_films_to_cache(
            self, films: list[ShortFilm],
            sort: str, page_size: int,
            page_number: int, genre: UUID | None
    ) -> None:
        """добавить фотсортированные фильмы в кеш"""
        ...


class FilmService:
    def __init__(
            self,
            film_cache_repository: FilmCacheRepositoryProtocol,
            film_repository: FilmRepositoryProtocol
    ):
        self._film_cache_repository = film_cache_repository
        self._film_repository = film_repository

    async def get_by_id(self, film_id: UUID) -> DetailFilm | None:
        film = await self._film_repository.get_by_id(film_id)
        if not film:
            film = await self._film_repository.get_by_id(film_id)
            if not film:
                logging.info(FILM_NOT_FOUND, 'id', film_id)
                return None
            await self._film_cache_repository.put_to_cache(name_id='film_id',
                                                           data=film)
        return film

    async def get_by_sort(
            self,
            sort: str,
            page_size: int,
            page_number: int,
            genre_id: UUID | None
    ) -> list[ShortFilm] | None:
        films = await self._film_cache_repository.get_by_sort(
            sort, page_size,
            page_number, genre_id
        )
        if not films:
            films = await self._film_repository.get_by_sort(sort,
                                                            page_size,
                                                            page_number,
                                                            genre_id)
            if not films:
                logging.info(FILM_NOT_FOUND, 'sort', sort)
                return None
            await self._film_cache_repository.put_sort_films_to_cache(
                films, sort, page_size,
                page_number, genre_id
            )
        return films

    async def get_by_title(self, film_title: str, page_size: int,
                           page_number: int) -> list[ShortFilm] | None:
        films = await self._film_repository.get_by_title(
            film_title, page_size, page_number
        )
        if not films:
            logging.info(FILM_NOT_FOUND, 'film_title', film_title)
            return None
        return films


@lru_cache()
def get_film_service(
        film_cache_repository: FilmCacheRepositoryProtocol = Depends(get_film_cache_repository),
        film_repository: FilmRepositoryProtocol = Depends(get_film_repository)
) -> FilmService:
    return FilmService(film_cache_repository, film_repository)
