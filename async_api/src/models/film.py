from typing import List

import orjson

from db.models.elastic_models import SerializedFilm
from .base import UUIDMixin


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


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
    description: str | None
    actors: List[Actor] | None
    writers: List[Writer] | None
    directors: List[Director] | None
    genre: List[Genre] | None

    @classmethod
    def from_serialized_movie(cls, serialized_movie: SerializedFilm):
        if serialized_movie.actors is None:
            actors = None
        else:
            actors = [
                Actor(uuid=actor.id, full_name=actor.name)
                for actor in serialized_movie.actors]

        if serialized_movie.writers is None:
            writers = None
        else:
            writers = [
                Writer(uuid=writer.id, full_name=writer.name)
                for writer in serialized_movie.writers
            ]

        if serialized_movie.director is None:
            directors = None
        else:
            directors = [
                Director(uuid=director.id, full_name=director.name)
                for director in serialized_movie.director
            ]
        if serialized_movie.genre is None:
            genre = None
        else:
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
