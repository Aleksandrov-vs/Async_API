from typing import List, Dict
from uuid import UUID

from pydantic import BaseModel


class SerializedFilm(BaseModel):
    id: UUID
    imdb_rating: float
    genre: List[str]
    title: str
    description: str
    director: List[str]
    actors_names: List[str]
    writers_names: List[str]
    actors: List[Dict]
    writers: List[Dict]