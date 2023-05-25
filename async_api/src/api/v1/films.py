from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from services.film import FilmService, get_film_service
from core.messages import FILM_NOT_FOUND, TOTAL_FILM_NOT_FOUND

router = APIRouter()


@router.get('/search', response_model=List[FilmSearch])
async def film_search(
        film_title: str = Query(
            'star',
            description="Название Кинопроизведения."),
        page_size: int = Query(
            50, gt=0, le=100,
            description="Количество записей на странице (от 1 до 100)."
        ),
        page_number: int = Query(
            1, gt=0, description="Номер страницы (начиная с 1)."
        ),
        film_service: FilmService = Depends(get_film_service)
) -> List[FilmSearch]:
    """
      возвращает список фильмов с похожим названием (с учетом пагинации):
      - **uuid**: id фильма
      - **title**: название фильма
      - **imdb_rating**: рейтинг фильма
    """

    films = await film_service.get_by_title(film_title, page_size, page_number)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=TOTAL_FILM_NOT_FOUND)
    return [FilmSearch(**film.dict()) for film in films]


@router.get('/{film_id}', response_model=Film)
async def film_details(
        film_id: str = Query(
            '025c58cd-1b7e-43be-9ffb-8571a613579b',
            description="UUID фильма"
        ),
        film_service: FilmService = Depends(get_film_service)) -> Film:
    """
    Возвращает информацию о фильме по его id:

    - **uuid**: id фильма
    - **title**: название фильма
    - **imdb_rating**: рейтинг фильма
    - **description**: описание фильма
    - **actors**: актеры
    - **writers**: сценаристы
    - **directors**:  режиссеры
    - **genre**: жанры
    """

    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=FILM_NOT_FOUND % ('film id', film_id))
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
    """
       Возвращает отсортированный список фильмов (с учетом пагинации и жанра):
       - **uuid**: id фильма
       - **title**: название фильма
       - **imdb_rating**: рейтинг фильма
    """

    films = await film_service.get_by_sort(sort, page_size,
                                           page_number, genre_id)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=TOTAL_FILM_NOT_FOUND)
    return [FilmSearch(**film.dict()) for film in films]
