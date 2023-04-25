import uuid
from dataclasses import dataclass


@dataclass
class UUIDModel:
    id: uuid.UUID


class PersonInFilm(UUIDModel):
    name: str


@dataclass
class ESMovies:
    id: uuid.UUID
    imdb_rating: float | None
    genre: list[str] | None
    title: str | None
    description: str | None
    director: list[str] | None
    actors_names: list[str] | None
    writers_names: list[str] | None
    actors: list[PersonInFilm] | None
    writers: list[PersonInFilm] | None
    modified: str | None
