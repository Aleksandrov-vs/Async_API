from dataclasses import dataclass
from typing import List, Dict, Union
from uuid import UUID


@dataclass
class Movie:
    id: UUID
    imdb_rating: float | None
    genre: List[str] | None
    title: str | None
    description: str | None
    director: List[str] | None
    actors_names: List[str] | None
    writers_names: List[str] | None
    actors: List[Dict[str, Union[UUID, str]]] | None
    writers: List[Dict[str, Union[UUID, str]]] | None
