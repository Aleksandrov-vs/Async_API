from pydantic import BaseModel


class Person(BaseModel):
    uuid: UUID
    full_name: str


class Genre(BaseModel):
    uuid: UUID
    name: str


class Film(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float
    description: str | None
    actors: List[Person] | None
    writers:  List[Person] | None
    directors:  List[Person] | None
    genre: List[Genre] | None


class FilmSearch(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float


class ResponseGenre(BaseModel):
    uuid: UUID
    name: str


class PersonFilm(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float
