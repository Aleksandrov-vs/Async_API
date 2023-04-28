from .base import BaseOrjsonModel


class Film(BaseOrjsonModel):
    """Полная информация по фильму."""
    title: str
    imdb_rating: float
    description: str | None
    genre: list[dict[str, str]] | None
    actors: list[dict[str, str]] | None
    writers: list[dict[str, str]] | None
    directors: list[dict[str, str]] | None


class Films(BaseOrjsonModel):
    """Модель главной страницы."""
    title: str
    imdb_rating: float
