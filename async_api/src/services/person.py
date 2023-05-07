import logging
from functools import lru_cache
from uuid import UUID

import orjson
from elasticsearch import NotFoundError, RequestError
from fastapi import Depends

from src.db.base import RedisBaseStorage, ElasticBaseStorage
from src.services.base_serivce import BaseService
from core.messages import (
    PERSON_NOT_FOUND,
    PERSON_NOT_FOUND_ES,
    PERSON_CACHE_NOT_FOUND
)
from Async_API_sprint_1.async_api.src.db.elastic_storage import get_elastic
from db.models.elastic_models import SerializedPerson, SerializedPersonFilm
from Async_API_sprint_1.async_api.src.db.redis_storage import get_redis
from models.person import Person, PersonFilms
from services.redis_utils import key_generate

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService(BaseService):
    def __init__(self, redis_storage: RedisBaseStorage, es_storage: ElasticBaseStorage):
        super().__init__(redis_storage, es_storage)

    async def get_by_id(self, person_id: UUID) -> Person | None:
        person = await self.get_data_from_redis(name_id='person_id',
                                                uuid=person_id,
                                                model=Person)
        if not person:
            ser_person = await self.get_data_from_elastic(index='persons',
                                                          uuid=person_id,
                                                          model=Person)
            if not ser_person:
                logging.info(PERSON_NOT_FOUND, 'person_id', person_id)
                return None
            person = Person.from_serialized_genre(ser_person)
            await self.put_data_to_redis(name_id='person_id',
                                         data=person)
        return person

    async def get_person_films(self, person_id) -> list[PersonFilms] | None:
        persons_film = await self._person_films_from_cache(person_id)
        if not persons_film:
            ser_films = await self._get_person_films_from_elastic(person_id)
            if not ser_films:
                logging.info(PERSON_NOT_FOUND, 'person_id', person_id)
                return None
            persons_film = [
                PersonFilms.from_serialized_genre(film)
                for film in ser_films
            ]
            await self._put_person_films_to_cache(person_id, persons_film)
        return persons_film

    async def search_person(
            self, person_name: str,
            page_size: int, page_number: int
    ) -> list[Person] | None:
        ser_persons = await self._search_person_from_elastic(person_name,
                                                             page_size,
                                                             page_number)
        if not ser_persons:
            logging.info(PERSON_NOT_FOUND, 'person_name', person_name)
            return None
        persons = [Person.from_serialized_genre(p) for p in ser_persons]
        return persons

    async def _get_person_from_elastic(
            self, person_id: UUID
    ) -> SerializedPerson | None:
        try:
            doc = await self.elastic.get('persons', person_id)
        except NotFoundError:
            logging.info(PERSON_NOT_FOUND_ES, 'person_id', person_id)
            return None
        return SerializedPerson(**doc['_source'])

    async def _get_person_films_from_elastic(
            self, person_id: UUID
    ) -> list[SerializedPersonFilm]:
        person_inf = await self._get_person_from_elastic(person_id)
        if person_inf is None:
            logging.info(PERSON_NOT_FOUND_ES, 'person_id', person_id)
            return None
        person_films_id = [f.id for f in person_inf.films]
        body = {
            "docs": [
                {
                    "_index": "movies",
                    "_id": f_id,
                    "_source": ["id", "title", "imdb_rating"]
                }
                for f_id in person_films_id
            ]
        }
        docs = await self.elastic.mget(index="movies", body=body)
        return [SerializedPersonFilm(**doc['_source']) for doc in docs['docs']]

    async def _search_person_from_elastic(
            self, person_name: str,
            page_size: int, page_number: int
    ) -> list[SerializedPerson] | None:
        q = {
            "match": {
                "full_name": {
                    "query": person_name, "fuzziness": "AUTO"
                }
            }
        }
        try:
            doc = await self.elastic.search(
                index='persons',
                body={
                    "query": q
                },
                from_=page_size * (page_number - 1),
                size=page_size
            )
        except NotFoundError:
            logging.info(PERSON_NOT_FOUND_ES, 'person_name', person_name)
            return None
        except RequestError:
            logging.info(PERSON_NOT_FOUND_ES, 'person_name', person_name)
            return None
        return [
            SerializedPerson(**doc['_source'])
            for doc in doc['hits']['hits']
        ]

    async def _put_person_to_cache(self, person: Person) -> None:
        key = await key_generate(person.uuid)
        await self.redis.set(key, person.json(),
                             PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def _person_from_cache(self, person_id: UUID) -> Person | None:
        key = await key_generate(person_id)
        data = await self.redis.get(key)
        if not data:
            logging.info(PERSON_CACHE_NOT_FOUND, 'person_id', person_id)
            return None
        person = Person.parse_raw(data)
        return person

    async def _person_films_from_cache(self, person_id: UUID) -> PersonFilms | None:
        key = await key_generate(person_id, source='person_films')
        data = await self.redis.get(key)
        if not data:
            logging.info(PERSON_CACHE_NOT_FOUND, 'person_id', person_id)
            return None
        return [PersonFilms.parse_raw(item) for item in orjson.loads(data)]

    async def _put_person_films_to_cache(self, person_id: UUID, person_films: list[PersonFilms]) -> None:
        key = await key_generate(person_id, source='person_films')
        await self.redis.set(key, orjson.dumps([person_film.json(by_alias=True) for person_film in person_films]),
                             PERSON_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
