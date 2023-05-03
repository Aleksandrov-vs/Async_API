from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from services.person import PersonService, get_person_service

router = APIRouter()


class PersonFilm(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float


@router.get('/{person_id}/film/', response_model=List[PersonFilm])
async def person_films(
        person_id: UUID,
        person_service: PersonService = Depends(get_person_service)
):
    films = await person_service.get_person_films(person_id)
    if films is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='persons film not found')
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
        person_id: UUID,
        person_service: PersonService = Depends(get_person_service)
):
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='person not found')
    return ResponsePerson(**person.dict())


@router.get('/search/', response_model=List[ResponsePerson])
async def search_person(
        person_name: str,
        page_size: int = Query(
            50, gt=0, le=100,
            description="Количество записей на странице (от 1 до 100)."
        ),
        page_number: int = Query(
            1, gt=0, description="Номер страницы (начиная с 1)."
        ),
        person_service: PersonService = Depends(get_person_service)
):
    persons = await person_service.search_person(person_name,
                                                 page_size,
                                                 page_number)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='person not found')
    return [ResponsePerson(**p.dict())for p in persons]
