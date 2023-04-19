import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from psycopg2.extensions import connection as _connection

from etl.utils.state import State


@dataclass
class ExtractProducer:
    id: uuid.UUID
    modified: datetime


class Producer:
    """ Класс для первоначальной выгрузки данных из базы данных """

    def __init__(self, conn: _connection, db_schema: str, table: str, state: State, state_key: str,
                 order_key: str = 'modified') -> None:
        """
        Инициализация класса
        :param conn: Подключение к базе данных
        :param db_schema: Схема данных
        :param table: Исходная таблица
        :param state: Объект состояния
        :param state_key: Ключ для проверки состояния
        :param order_key: Ключ для фильтрации
        """
        self.conn = conn

        self.schema = db_schema
        self.table = table

        self.state = state
        self.state_key = state_key
        self.last_state = None

        self.order_key = order_key

    def generate_sql(self) -> str:
        """
        Функция генерации sql запроса для сбора данных
        :return: Текст sql запроса
        """
        self.last_state = self.state.get_state(self.state_key)
        request = f"""
        SELECT id, modified
        FROM {self.schema}.{self.table}
        WHERE modified > '{self.last_state}'
        ORDER BY {self.order_key};
        """
        return request

    def get_data(self) -> Iterable[ExtractProducer]:
        """
        Генератор для сбора данных
        :return: Объекты класса ExtractProducer
        """
        stmt = self.generate_sql()
        with self.conn.cursor() as cur:
            cur.execute(stmt)
            for row in cur.fetchall():
                self.state.set_state(self.state_key, row['modified'].strftime('%Y-%m-%d %H:%M:%S.%f %z'))
                yield ExtractProducer(**row)
