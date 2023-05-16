from typing import List
from uuid import UUID

from pydantic import BaseModel


class Person(BaseModel):
    id: UUID
    name: str


class SerializedGenre(BaseModel):
    id: UUID
    name: str


class SerializedFilm(BaseModel):
    id: UUID
    imdb_rating: float
    genre: List[SerializedGenre] | List
    title: str
    description: str | None
    director: List[Person] | None
    actors_names: List[str] | None
    writers_names: List[str] | None
    actors: List[Person] | None
    writers: List[Person] | None


class PersonFilms(BaseModel):
    id: UUID
    roles: List[str]
    title: str


class SerializedPerson(BaseModel):
    id: UUID
    full_name: str
    films: List[PersonFilms]


class SerializedPersonFilm(BaseModel):
    id: UUID
    title: str
    imdb_rating: float
