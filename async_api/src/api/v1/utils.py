from fastapi import Query


class PaginateQueryParams:
    """Dependency class to parse pagination query params."""

    def __init__(
        self,
        page_number: int = Query(
            1,
            title="Page number.",
            description="Номер страницы (начиная с 1)",
            gt=0,
        ),
        page_size: int = Query(
            50,
            title="Size of page.",
            description="Количество записей на странице (от 1 до 100)",
            gt=0,
            le=100,
        ),
    ):
        self.page_number = page_number
        self.page_size = page_size
