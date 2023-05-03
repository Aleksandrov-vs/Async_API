from uuid import UUID

from db.models.elastic_models import SerializedGenre

from .base import BaseOrjsonModel


class Genre(BaseOrjsonModel):
    """Список жанров."""
    uuid: UUID
    name: str

    @classmethod
    def from_serialized_genre(cls, serialized_genre: SerializedGenre):
        return cls(
            uuid=serialized_genre.id,
            name=serialized_genre.name
        )
