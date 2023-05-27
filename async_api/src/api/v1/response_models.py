from uuid import UUID
from pydantic import BaseModel

# Модели films.py
class Person(BaseModel):
    uuid: UUID
    full_name: str


class Genre(BaseModel):
    uuid: UUID
    name: str


class Film(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float
    description: str | None
    actors: list[Person] | None
    writers: list[Person] | None
    directors: list[Person] | None
    genre: list[Genre] | None


class FilmSearch(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float


# Модель genres.py
class ResponseGenre(BaseModel):
    uuid: UUID
    name: str


# Модели persons.py
class PersonFilm(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float


class ResponsePersonRoles(BaseModel):
    uuid: UUID
    roles: list[str]


class ResponsePerson(BaseModel):
    uuid: UUID
    full_name: str
    films: list[ResponsePersonRoles]
