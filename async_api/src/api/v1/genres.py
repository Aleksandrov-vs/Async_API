from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from services.genre import GenreService, get_genre_service
from core.messages import GENRE_NOT_FOUND, TOTAL_GENRES_NOT_FOUND

router = APIRouter()


@router.get('/', response_model=list[ResponseGenre])
async def get_genres(genre_service: GenreService = Depends(get_genre_service)):
    """
       Возвращает список всех жанров одним списком:
       - **uuid**: id жанра
       - **name**: название жанра
    """
    genres = await genre_service.get_all()
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=TOTAL_GENRES_NOT_FOUND)
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
                            detail=GENRE_NOT_FOUND % ('genre id', genre_id))
    return ResponseGenre(**genre.dict())
