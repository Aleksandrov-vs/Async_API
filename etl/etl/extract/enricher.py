import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator, List, Union
import logging
from more_itertools import ichunked
from psycopg2.extensions import connection as _connection

from etl.extract.merger import ExtractMerger
from etl.extract.producer import ExtractProducer


@dataclass
class ExtractEnricher:
    fw_id: uuid.UUID
    title: str
    description: str
    rating: float
    type: str
    created: datetime
    modified: datetime
    role: str
    person_id: uuid.UUID
    person_full_name: str
    genre: str


class Enricher:
    """ Класс для обогощения данных """

    def __init__(self, conn: _connection, data: Iterator[Union[ExtractMerger, ExtractProducer]], db_schema: str,
                 batch_size: int = 1000) -> None:
        """
        Инициализация класса
        :param conn: Подключение к базе данных
        :param data: Данные для обогащения
        :param db_schema: Схема данных
        :param batch_size: Размер батча
        """
        self.conn = conn

        self.data = data

        self.schema = db_schema
        self.batch = batch_size

        self.last_order_value = None

    def generate_sql(self, foreign_keys: List[uuid.UUID]) -> str:
        """
        Функция для генерации sql запросов
        :param foreign_keys: Список внешних ключей
        :return: Текст sql запроса
        """
        if self.last_order_value:
            if_id = f"AND fw.id > '{self.last_order_value}'"
        else:
            if_id = ""
        if foreign_keys:
            logging.info('Enricher: ' + str(len(foreign_keys)))
            fk_values = ', '.join(map(lambda x: f"'{str(x)}'", foreign_keys))
            fk_ids = f"WHERE fw.id IN ({fk_values})"
        else:
            return None
        request = f"""
            SELECT DISTINCT
            fw.id as fw_id,
            fw.title,
            fw.description,
            fw.rating,
            fw.type,
            fw.created,
            fw.modified,
            pfw.role,
            p.id as person_id,
            p.full_name as person_full_name,
            g.name as genre
            FROM {self.schema}.film_work fw
            LEFT JOIN {self.schema}.person_film_work pfw ON pfw.film_work_id = fw.id
            LEFT JOIN {self.schema}.person p ON p.id = pfw.person_id
            LEFT JOIN {self.schema}.genre_film_work gfw ON gfw.film_work_id = fw.id
            LEFT JOIN {self.schema}.genre g ON g.id = gfw.genre_id
            {fk_ids}
            {if_id}
            ORDER BY fw.id
            LIMIT {self.batch};
        """
        return request

    def get_data(self) -> Iterator[ExtractEnricher]:
        """
        Функция сбора данных по сформированным запросам
        :return: Объекты класса ExtractEnricher
        """
        for chunk in ichunked(self.data, self.batch):
            self.last_order_value = None
            ids = [row.id for row in chunk]
            while True:
                stmt = self.generate_sql(ids)
                if not stmt:
                    break
                with self.conn.cursor() as cur:
                    cur.execute(stmt)
                    if not cur.rowcount:
                        break
                    for row in cur.fetchall():
                        yield ExtractEnricher(**row)
                self.last_order_value = row['fw_id']
