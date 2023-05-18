import logging
from functools import lru_cache
from typing import Protocol
from uuid import UUID

from fastapi import Depends

from db.elastic.person import get_person_repository
from core.messages import (
    PERSON_NOT_FOUND,
)
from db.redis.person import get_person_cache_repository
from models.person import Person, PersonFilm


class PersonRepositoryProtocol(Protocol):
    async def get_by_id(self, person_id: UUID) -> Person | None:
        """Возвращает описание персоны по id"""
        ...

    async def search_by_name(
            self,
            person_name: str,
            page_size: int,
            page_number: int
    ) -> list[Person] | None:
        """Возвращает список персон с похожим именем"""
        ...

    async def get_films_for_person(
            self, person_id: UUID
    ) -> list[PersonFilm] | None:
        """Возвращает все фильмы в которых участвовала персона"""
        ...


class PersonCacheRepositoryProtocol(Protocol):
    async def get_by_id(
            self,
            person_id: UUID
    ) -> Person | None:
        """Возвращает персону из кеш по id"""
        ...

    async def get_person_films(
            self,
            person_id: UUID
    ) -> list[PersonFilm] | None:
        """Возвращает все фильмы в которых участвовала персона из кеш"""
        ...

    async def put_person_films(
            self,
            person_id: UUID,
            person_films: list[PersonFilm] | None
    ) -> None:
        """Добавить фильмы в которых участвовала персона в кеш"""
        ...

    async def put_person(self, person: Person) -> None:
        """Добавить в кеш персону"""
        ...


class PersonService:
    def __init__(
            self,
            person_cache_repository: PersonCacheRepositoryProtocol,
            person_repository: PersonRepositoryProtocol):
        self._person_cache_repository = person_cache_repository
        self._person_repository = person_repository

    async def get_by_id(self, person_id: UUID) -> Person | None:
        person = await self._person_cache_repository.get_by_id(
            person_id
        )
        if not person:
            person = await self._person_repository.get_by_id(person_id)
            if not person:
                logging.info(PERSON_NOT_FOUND, 'person_id', person_id)
                return None
            await self._person_cache_repository.put_person(person)
        return person

    async def get_films_for_person(self, person_id) -> list[PersonFilm] | None:
        films_for_person = await self._person_cache_repository.get_person_films(person_id)
        if not films_for_person:
            films_for_person = await self._person_repository.get_films_for_person(person_id)
            if not films_for_person:
                logging.info(PERSON_NOT_FOUND, 'person_id', person_id)
                return None
            await self._person_cache_repository.put_person_films(
                person_id, films_for_person
            )
        return films_for_person

    async def search_person(
            self, person_name: str,
            page_size: int, page_number: int
    ) -> list[Person] | None:
        persons = await self._person_repository.search_by_name(
            person_name,
            page_size,
            page_number
        )
        if not persons:
            logging.info(PERSON_NOT_FOUND, 'person_name', person_name)
            return None
        return persons


@lru_cache()
def get_person_service(
        person_cache_repository: PersonCacheRepositoryProtocol = Depends(get_person_cache_repository),
        person_repository: PersonRepositoryProtocol = Depends(get_person_repository)
) -> PersonService:
    return PersonService(person_cache_repository, person_repository)
