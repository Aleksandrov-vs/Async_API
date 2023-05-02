from typing import Dict, List
from uuid import UUID

from pydantic import BaseModel, Field


class Person(BaseModel):
    id: UUID
    name: str


class Genre(BaseModel):
    id: UUID
    name: str


class SerializedFilm(BaseModel):
    id: UUID
    imdb_rating: float
    genre: List[Genre]
    title: str
    description: str | None
    director: List[Person]
    actors_names: List[str]
    writers_names: List[str]
    actors: List[Person]
    writers: List[Person]
