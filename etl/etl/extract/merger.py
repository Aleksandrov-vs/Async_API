import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator, List
import logging

from psycopg2.extensions import connection as _connection

from etl.extract.producer import ExtractProducer


@dataclass
class ExtractMerger:
    id: uuid.UUID
    modified: datetime


class Merger:
    """ Класс для склейки данных по внешнему ключу """

    def __init__(self, conn: _connection, producer: Iterator[ExtractProducer], db_schema: str, base_table: str,
                 base_table_id: str, merge_table: str, merge_table_id: str, merge_table_fk: str,
                 batch_size: int = 1000) -> None:
        """
        Инициализация класса
        :param conn: Подключение к базе данных
        :param producer: Генератор полученный в Producer
        :param db_schema: Схема данных
        :param base_table: Базовая таблица
        :param base_table_id: Поле первичного ключа базовой таблицы
        :param merge_table: Таблица для склейки
        :param merge_table_id: Поле первичного ключа таблицы для мерджа
        :param merge_table_fk: Поле внешнего ключа таблицы для мерджа
        :param batch_size: Размер батча
        """
        self.conn = conn

        self.producer = producer

        self.schema = db_schema
        self.base_table = base_table
        self.base_table_id = base_table_id
        self.merge_table = merge_table
        self.merge_table_id = merge_table_id
        self.merge_table_fk = merge_table_fk
        self.batch = batch_size

        self.last_order_value = None

    def generate_sql(self, foreign_keys: List[uuid.UUID]) -> str:
        """
        Функция для генерации sql запроса, учитывая входные данные
        :param foreign_keys: Список внешних ключей
        :return: Текст sql запроса
        """
        if self.last_order_value:
            if_id = f"AND bt.{self.base_table_id} > '{self.last_order_value}'"
        else:
            if_id = ""
        if foreign_keys:
            fk_values = ', '.join(map(lambda x: f"'{str(x)}'", foreign_keys))
            fk_ids = f"WHERE mt.{self.merge_table_id} in ({fk_values})"
        else:
            return None
        request = f"""
        SELECT DISTINCT bt.id, bt.modified
        FROM {self.schema}.{self.base_table} bt
        LEFT JOIN {self.schema}.{self.merge_table} mt ON mt.{self.merge_table_fk} = bt.{self.base_table_id}
        {fk_ids}
        {if_id}
        ORDER BY bt.{self.base_table_id}
        LIMIT {self.batch};
        """
        return request

    def get_data(self) -> Iterator[ExtractMerger]:
        """
        Сбор данных по сформированному запросу
        :return: Генератор объектов формата ExtractMerger
        """
        ids = [row.id for row in self.producer]
        while True:
            stmt = self.generate_sql(ids)
            if not stmt:
                break
            with self.conn.cursor() as cur:
                cur.execute(stmt)
                if not cur.rowcount:
                    break
                for row in cur.fetchall():
                    yield ExtractMerger(**row)
            self.last_order_value = row[self.base_table_id]
