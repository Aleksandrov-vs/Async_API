import logging
from uuid import UUID
from typing import List

from core.messages import PERSON_NOT_FOUND_ES
from .base import BaseElasticStorage
from db.models.elastic_models import SerializedPerson, SerializedPersonFilm
from models.person import Person, PersonFilm


class PersonElasticRepository(BaseElasticStorage):
    async def get_by_id(self, person_id: UUID) -> Person | None:
        person: SerializedPerson = await self._get_by_id(
            'persons',
            person_id,
            SerializedPerson
        )
        if person is None:
            logging.info(PERSON_NOT_FOUND_ES, 'person_id', person_id)
            return None
        return Person.from_serialized_person(person)

    async def search_by_name(
            self,
            person_name: str,
            page_size: int,
            page_number: int) -> List[Person] | None:
        q = {
            "match": {
                "full_name": {
                    "query": person_name, "fuzziness": "AUTO"
                }
            }
        }
        body_of_q = {"query": q}
        doc = await self._search(
            index='persons',
            body_of_query=body_of_q,
            page_number=page_number,
            size=page_size
        )
        if doc is None:
            logging.info(PERSON_NOT_FOUND_ES, 'person_name', person_name)
            return None
        ser_person = [
            SerializedPerson(**p['_source'])
            for p in doc
        ]
        return [
            Person.from_serialized_person(s_p)
            for s_p in ser_person
        ]

    async def get_films_for_person(self, person_id: UUID) -> list[PersonFilm] | None:
        person = await self.get_by_id(person_id)
        if person is None:
            logging.info(PERSON_NOT_FOUND_ES, 'person_id', person_id)
            return None
        person_films_id = [f.uuid for f in person.films]
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
        ser_film_for_person = [SerializedPersonFilm(**doc['_source']) for doc in docs['docs']]

        film_for_person = [
            PersonFilm.from_serialized_genre(s_p) for s_p in ser_film_for_person
        ]
        return film_for_person


person_repository: PersonElasticRepository | None = None


def get_person_repository() -> PersonElasticRepository:
    return person_repository
