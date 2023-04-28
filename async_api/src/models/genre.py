from .base import BaseOrjsonModel


class Genre(BaseOrjsonModel):
    """Список жанров."""
    name: str
