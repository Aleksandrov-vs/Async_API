from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from services.film import FilmService, get_film_service

router = APIRouter()


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
    description: str
    actors: List[Person]
    writers:  List[Person]
    directors:  List[Person]
    genre: List[Genre]


class FilmSearch(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float


@router.get('/search', response_model=List[FilmSearch])
async def film_search(
        film_title: str,
        page_size: int = Query(
            50, gt=0, le=100,
            description="Количество записей на странице (от 1 до 100)."
        ),
        page_number: int = Query(
            1, gt=0, description="Номер страницы (начиная с 1)."
        ),
        film_service: FilmService = Depends(get_film_service)
) -> List[FilmSearch]:

    films = await film_service.get_by_query(film_title, page_size, page_number)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='films not found')
    return [FilmSearch(**film.dict()) for film in films]


@router.get('/{film_id}', response_model=Film)
async def film_details(
        film_id: str,
        film_service: FilmService = Depends(get_film_service)) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='film not found')
    return Film(**film.dict())


@router.get('/', response_model=List[FilmSearch])
async def films_sort(
        sort: str = Query(
            '-imdb_rating', regex='^-imdb_rating$|^imdb_rating$',
            description="Сортировка в формате поле-порядок (-по убыванию, "
                        "без знака - по возрастанию)."
        ),
        page_size: int = Query(
            50, gt=0, le=100,
            description="Количество записей на странице (от 1 до 100)."
        ),
        page_number: int = Query(
            1, gt=0, description="Номер страницы (начиная с 1)."
        ),
        genre_id: UUID | None = Query(
            None, description="id Жанра"
        ),
        film_service: FilmService = Depends(get_film_service)) \
        -> List[FilmSearch]:
    films = await film_service.get_by_sort(sort, page_size,
                                           page_number, genre_id)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='film not found')
    return [FilmSearch(**film.dict()) for film in films]
