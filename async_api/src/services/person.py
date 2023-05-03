import logging
from functools import lru_cache
from typing import List, Optional
from uuid import UUID

import orjson
from db.elastic import get_elastic
from db.models.elastic_models import SerializedPerson, SerializedPersonFilm
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.person import Person, PersonFilms
from redis.asyncio import Redis
from services.redis_utils import key_generate

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: UUID) -> Optional[Person]:
        person = await self._person_from_cache(person_id)
        if not person:
            ser_person = await self._get_person_from_elastic(person_id)
            if not ser_person:
                logging.info(f'Person {person_id} is not found!')
                return None
            person = Person.from_serialized_genre(ser_person)
            await self._put_person_to_cache(person)
        return person

    async def get_person_films(self, person_id) -> Optional[List[PersonFilms]]:
        persons_film = await self._person_films_from_cache(person_id)
        if not persons_film:
            ser_films = await self._get_person_films_from_elastic(person_id)
            if not ser_films:
                logging.info(f'Person {person_id} is not found!')
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
    ) -> Optional[List[Person]]:
        ser_persons = await self._search_person_from_elastic(person_name,
                                                             page_size,
                                                             page_number)
        if not ser_persons:
            logging.info('Person is not found!')
            return None
        persons = [Person.from_serialized_genre(p) for p in ser_persons]
        return persons

    async def _get_person_from_elastic(
            self, person_id: UUID
    ) -> Optional[SerializedPerson]:
        try:
            doc = await self.elastic.get('persons', person_id)
        except NotFoundError:
            logging.error(f'Elastic not found error!')
            return None
        return SerializedPerson(**doc['_source'])

    async def _get_person_films_from_elastic(
            self, person_id: UUID
    ) -> Optional[List[SerializedPersonFilm]]:
        person_inf = await self._get_person_from_elastic(person_id)
        if person_inf is None:
            logging.error(f'Elastic not found error!')
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
    ) -> Optional[List[SerializedPerson]]:

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
            logging.error(f'Elastic not found error!')
            return None
        return [
            SerializedPerson(**doc['_source'])
            for doc in doc['hits']['hits']
        ]

    async def _put_person_to_cache(self, person: Person):
        key = await key_generate(person.uuid)
        await self.redis.set(key, person.json(),
                             PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def _person_from_cache(self, person_id: UUID) -> Optional[Person]:
        key = await key_generate(person_id)
        data = await self.redis.get(key)
        if not data:
            logging.error(f'Cache is empty...')
            return None
        person = Person.parse_raw(data)
        return person

    async def _person_films_from_cache(self, person_id: UUID) -> Optional[PersonFilms]:
        key = await key_generate(person_id, source='person_films')
        data = await self.redis.get(key)
        if not data:
            logging.error(f'Cache is empty...')
            return None
        return [PersonFilms.parse_raw(item) for item in orjson.loads(data)]

    async def _put_person_films_to_cache(self, person_id: UUID, person_films: List[PersonFilms]) -> None:
        key = await key_generate(person_id, source='person_films')
        await self.redis.set(key, orjson.dumps([person_film.json(by_alias=True) for person_film in person_films]),
                             PERSON_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
