import logging
from uuid import UUID

from orjson import orjson

from core.messages import PERSON_CACHE_NOT_FOUND
from db.redis.base import RedisStorage
from models.person import Person, PersonFilm


class PersonCacheRepository(RedisStorage):
    async def get_by_id(self, person_id: UUID) -> Person | None:
        key = self._key_generate(person_id)
        data = await self.redis.get(key)
        if not data:
            logging.info(PERSON_CACHE_NOT_FOUND, 'person_id', person_id)
            return None
        person = Person.parse_raw(data)
        return person

    async def get_person_films(self, person_id: UUID) -> list[PersonFilm] | None:
        key = self._key_generate(person_id, source='person_films')
        data = await self.redis.get(key)
        if not data:
            logging.info(PERSON_CACHE_NOT_FOUND, 'person_id', person_id)
            return None
        return [PersonFilm.parse_raw(item) for item in orjson.loads(data)]

    async def put_person_films(self, person_id: UUID, person_films: list[PersonFilm]) -> None:
        key = self._key_generate(person_id, source='person_films')
        await self.redis.set(
            key,
            orjson.dumps([person_film.json(by_alias=True) for person_film in person_films])
        )

    async def put_person(self, person: Person) -> None:
        key = self._key_generate(person.uuid)
        await self.redis.set(
            key, person.json()
        )


person_cache_repository: PersonCacheRepository | None = None


def get_person_cache_repository() -> PersonCacheRepository:
    return person_cache_repository
