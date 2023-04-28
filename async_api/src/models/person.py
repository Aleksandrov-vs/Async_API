from .base import BaseOrjsonModel


class Person(BaseOrjsonModel):
    """Данные по персоне."""
    full_name: str
    films: list[dict[str, str | list[str]]] | None
