from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from services.genre import GenreService, get_genre_service

router = APIRouter()


class ResponseGenre(BaseModel):
    uuid: UUID
    name: str


@router.get('/', response_model=List[ResponseGenre])
async def get_genres(genre_service: GenreService = Depends(get_genre_service)):
    """
       Возвращает список всех жанров одним списком:
       - **uuid**: id жанра
       - **name**: название жанра
    """
    genres = await genre_service.get_all()
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='genres not found')
    return [ResponseGenre(**genre.dict()) for genre in genres]


@router.get('/{genre_id}', response_model=ResponseGenre)
async def detail_genre(
        genre_id: UUID = Query(
            '6c162475-c7ed-4461-9184-001ef3d9f26e',
            description=' UUID жанра',
        ),
        genre_service: GenreService = Depends(get_genre_service)
):
    """
           Возвращает информацию о жанре по его id:
           - **uuid**: id жанра
           - **name**: название жанра
    """

    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='genre not found')
    return ResponseGenre(**genre.dict())
