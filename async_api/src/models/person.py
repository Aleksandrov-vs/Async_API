from typing import List

from db.models.elastic_models import SerializedPerson, SerializedPersonFilm

from .base import UUIDMixin


class PersonRoleInFilm(UUIDMixin):
    """Фильмы персоны"""
    roles: List[str]


class Person(UUIDMixin):
    """Данные по персоне."""
    full_name: str
    films: List[PersonRoleInFilm] | None

    @classmethod
    def from_serialized_person(cls, serialized_person: SerializedPerson):
        return cls(
            uuid=serialized_person.id,
            full_name=serialized_person.full_name,
            films=[
                PersonRoleInFilm(uuid=f.id, roles=f.roles)
                for f in serialized_person.films
            ]
        )


class PersonFilm(UUIDMixin):
    title: str
    imdb_rating: str

    @classmethod
    def from_serialized_genre(
            cls,
            serialized_person_film: SerializedPersonFilm
    ):
        return cls(
            uuid=serialized_person_film.id,
            title=serialized_person_film.title,
            imdb_rating=serialized_person_film.imdb_rating
        )
