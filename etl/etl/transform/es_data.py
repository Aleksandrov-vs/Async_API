from typing import Iterable

from etl.extract.enricher import ExtractEnricher
from .models import Movie


class TransformETL:
    """ Класс для трансформации данных в формат elasticsearch """

    def __init__(self, data: Iterable[ExtractEnricher]) -> None:
        """
        Инициалихация класса
        :param data: Входные данные
        """
        self.data = data
        self.last_row = None
        self.directors = None
        self.actors = None
        self.writers = None
        self.genres = None

    def null_containers(self) -> None:
        """
        Служебная функция для очистки контейнеров класса
        """
        self.directors = set()
        self.actors = set()
        self.writers = set()
        self.genres = set()

    def add_person(self, row: ExtractEnricher) -> None:
        """
        Функция для добавления персоны в соотвествующий его роли контейнер
        :param row: Строка в формате даакласса
        """
        if row.role == 'actor':
            self.actors.add((('id', row.person_id), ('name', row.person_full_name)))
        elif row.role == 'writer':
            self.writers.add((('id', row.person_id), ('name', row.person_full_name)))
        elif row.role == 'director':
            self.directors.add(row.person_full_name)

    def movie_from_row(self, row: ExtractEnricher) -> Iterable[Movie]:
        """
        Генератор объектов класса Movie
        :param row: Строка в формате датакласса
        :return: Объекты класса Movie
        """
        actors = [dict(pair) for pair in self.actors]
        writers = [dict(pair) for pair in self.writers]
        movie = Movie(
            id=row.fw_id,
            imdb_rating=row.rating,
            genre=list(self.genres),
            title=row.title,
            description=row.description,
            director=list(self.directors),
            actors_names=[actor['name'] for actor in actors],
            writers_names=[writer['name'] for writer in writers],
            actors=actors,
            writers=writers
        )
        yield movie

    def transform_data(self) -> Iterable[Movie]:
        """
        Главная генеративная функция для трансформации данных
        :return: Объекты класса Movie
        """
        self.null_containers()
        for row in self.data:
            if not self.last_row:
                self.last_row = row
            if self.last_row.fw_id != row.fw_id:
                yield from self.movie_from_row(self.last_row)
                self.last_row = row
                self.null_containers()
            self.add_person(row)
            self.genres.add(row.genre)
        if self.last_row:
            yield from self.movie_from_row(self.last_row)
