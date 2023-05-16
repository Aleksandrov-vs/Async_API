from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from services.person import PersonService, get_person_service
from core.messages import TOTAL_PERSON_NOT_FOUND, PERSON_NOT_FOUND, PERSONS_FILMS_NOT_FOUND

router = APIRouter()


class PersonFilm(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float


@router.get('/{person_id}/film/', response_model=List[PersonFilm])
async def person_films(
        person_id: UUID = Query(
            'a5a8f573-3cee-4ccc-8a2b-91cb9f55250a',
            description='UUID персоны'
        ),
        person_service: PersonService = Depends(get_person_service)
):
    """
       Возвращает список фильмов в создании которых приняла участие персона с переданным id:
       - **uuid**: id фильма
       - **name**: название фильма
    """
    films = await person_service.get_films_for_person(person_id)
    if films is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=PERSONS_FILMS_NOT_FOUND)
    return films


class ResponsePersonRoles(BaseModel):
    uuid: UUID
    roles: List[str]


class ResponsePerson(BaseModel):
    uuid: UUID
    full_name: str
    films: List[ResponsePersonRoles]


@router.get('/{person_id}', response_model=ResponsePerson)
async def detail_person(
        person_id: UUID = Query(
            'a5a8f573-3cee-4ccc-8a2b-91cb9f55250a',
            description='UUID персоны'
        ),
        person_service: PersonService = Depends(get_person_service)
):
    """
       Возвращает детальную информацию о персоне по его id:
       - **uuid**: id персоны
       - **full_name**: полное имя персоны
       - **films**: список фильмов в которых уччастовала персона (id фильма и роль)
    """
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=PERSON_NOT_FOUND % ('person_id', person_id))
    return ResponsePerson(**person.dict())


@router.get('/search/', response_model=List[ResponsePerson])
async def search_person(
        person_name: str = Query(
            'George Lucas',
            description='Имя персоны для нечеткого поиска'
        ),
        page_size: int = Query(
            50, gt=0, le=100,
            description="Количество записей на странице (от 1 до 100)."
        ),
        page_number: int = Query(
            1, gt=0, description="Номер страницы (начиная с 1)."
        ),
        person_service: PersonService = Depends(get_person_service)
):
    """
       Возвращает список персон с похожими именами (с учетом пагинации):
       - **uuid**: id персоны
       - **full_name**: полное имя персоны
       - **films**: список фильмов в которых участовала персона (id фильма и роль)
    """
    persons = await person_service.search_person(person_name,
                                                 page_size,
                                                 page_number)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=TOTAL_PERSON_NOT_FOUND)
    return [ResponsePerson(**p.dict())for p in persons]
