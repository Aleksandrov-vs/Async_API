import uuid
from uuid import UUID
import orjson

from typing import List, Tuple, Dict
# Используем pydantic для упрощения работы при перегонке данных из json в объекты
from pydantic import Field

from db.models.elastic_models import SerializedFilm
from .base import BaseOrjsonModel


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class UUIDMixin(BaseOrjsonModel):
    uuid: UUID


class Actor(UUIDMixin):
    full_name: str


class Writer(Actor):
    pass


class Director(UUIDMixin):
    full_name: str


class Genre(UUIDMixin):
    name: str


class ShortFilm(UUIDMixin):
    title: str
    imdb_rating: float

    @classmethod
    def from_serialized_movie(cls, serialized_movie: SerializedFilm):
        return cls(
            uuid=serialized_movie.id,
            title=serialized_movie.title,
            imdb_rating=serialized_movie.imdb_rating,
        )


class DetailFilm(ShortFilm):
    description: str
    actors: List[Actor]
    writers: List[Writer]
    directors: List[Director]
    genre: List[Genre]

    @classmethod
    def from_serialized_movie(cls, serialized_movie: SerializedFilm):
        actors = [Actor(uuid=actor.get('id'), full_name=actor.get('name')) for actor in serialized_movie.actors]
        writers = [Writer(uuid=writer.get('id'), full_name=writer.get('name')) for writer in serialized_movie.writers]
        directors = [Director(full_name=director[0]) for director in serialized_movie.director]
        genre = [Genre(name=g) for g in serialized_movie.genre]
        return cls(
            uuid=serialized_movie.id,
            title=serialized_movie.title,
            imdb_rating=serialized_movie.imdb_rating,
            description=serialized_movie.description,
            genre=genre,
            actors=actors,
            writers=writers,
            directors=directors,
        )
