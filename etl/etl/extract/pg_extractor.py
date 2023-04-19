import logging
from datetime import datetime, timezone
from typing import Dict, Any, Iterable

from psycopg2.extensions import connection as _connection

from etl.extract.enricher import Enricher, ExtractEnricher
from etl.extract.merger import Merger
from etl.extract.producer import Producer
from etl.utils.state import State


class PostgresExtractor:
    """ Класс для выгрузки данных из Postgresql """

    def __init__(self, conn: _connection, state: State) -> None:
        """
        Инициализация класса
        :param conn: Подключение к базе данных
        :param state: Объект состояния
        """
        self.state = state
        self.conn = conn
        self.null_date = datetime(1, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f %z')

    def set_base_state(self, state_key: str) -> None:
        """
        Функция для проверки на нулевое значение состояния
        :param state_key: Ключ состояния
        """
        if not self.state.get_state(state_key):
            self.state.set_state(state_key, self.null_date)

    def get_task(self, task_config: Dict[str, Any]) -> Iterable[ExtractEnricher]:
        """
        Генератор для выгрузки данных по заданию
        :param task_config:
        :return:
        """
        self.set_base_state(task_config['producer']['state_key'])
        producer, merger, enricher = None, None, None
        try:
            producer = Producer(conn=self.conn, state=self.state, **task_config['producer']).get_data()
        except RuntimeError:
            logging.error('Bad EXTRACT_CONFIG: producer')
        if task_config.get('merger') and producer:
            try:
                merger = Merger(conn=self.conn, producer=producer, **task_config['merger']).get_data()
            except RuntimeError:
                logging.error('Bad EXTRACT_CONFIG: merger')
        if merger:
            data = merger
        elif producer:
            data = producer
        else:
            logging.error('Bad EXTRACT_CONFIG: structure')
            return None
        try:
            enricher = Enricher(conn=self.conn, data=data, **task_config['enricher']).get_data()
        except RuntimeError:
            logging.error('Bad EXTRACT_CONFIG: merger')
        yield from enricher

    def get_data(self, routine_config: Dict[str, Any]) -> Iterable[ExtractEnricher]:
        for key in routine_config:
            logging.info(f'Getting data from {key} source')
            config = routine_config[key]
            result = self.get_task(config)
            yield from result
