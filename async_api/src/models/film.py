from typing import List
from uuid import UUID

import orjson

from db.models.elastic_models import SerializedFilm
from .base import BaseOrjsonModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class UUIDMixin(BaseOrjsonModel):
    uuid: UUID


class Actor(UUIDMixin):
    full_name: str


class Writer(Actor):
    pass


class Director(Actor):
    pass


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
        print(serialized_movie.genre)
        actors = [
            Actor(uuid=actor.id, full_name=actor.name)
            for actor in serialized_movie.actors]
        writers = [
            Writer(uuid=writer.id, full_name=writer.name)
            for writer in serialized_movie.writers
        ]
        directors = [
            Director(uuid=director.id, full_name=director.name)
            for director in serialized_movie.director
        ]
        print(serialized_movie.genre)
        genre = [
            Genre(uuid=g.id, name=g.name)
            for g in serialized_movie.genre
        ]
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
