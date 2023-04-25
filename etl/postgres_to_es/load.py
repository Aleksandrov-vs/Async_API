import time
import logging
from typing import List, Iterator, Tuple, Optional

import elasticsearch
from elasticsearch import Elasticsearch, helpers

from backoff_decorator import backoff
from settings import ElasticConfig
from state import State
from schema import ESMovies
from es_index import INDEX_MOVIES


logger = logging.getLogger(__name__)


class ElasticLoader:
    def __init__(
        self,
        state: State,
        config: ElasticConfig,
        index: str,
        elastic_conn: Optional[Elasticsearch] = None,
    ) -> None:
        self.state = state
        self.config = config
        self.index = index
        self.elastic_conn = elastic_conn

    @property
    def elastic_connection(self) -> Elasticsearch:
        """Вернуть текущее подключение для ES или инициализировать новое"""
        try:
            if self.elastic_conn is None or not self.elastic_conn.ping():
                self.elastic_conn = self.create_connection()
        except elasticsearch.exceptions.ConnectionError as er:
            logger.error('Elasticserarch connection error: %s', er)
            return
        return self.elastic_conn

    @backoff(start_sleep_time=0.5)
    def create_connection(self) -> Elasticsearch:
        """Создать новое подключение для ES"""
        return Elasticsearch(
            host=self.config.host,
            port=self.config.port,
            scheme=self.config.scheme
            )

    @backoff(start_sleep_time=0.5)
    def create_index_if_not_exists(self) -> None:
        """Создаёт индекс, если его не существовало."""
        try:
            self.elastic_connection.indices.create(
                index=self.index,
                body=INDEX_MOVIES
            )
        except elasticsearch.exceptions.RequestError as er:
            if er.error == 'resource_already_exists_exception':
                pass

    @backoff(start_sleep_time=0.5)
    def generate_docs(
        self, docs: Iterator[List[ESMovies]]
    ) -> Iterator[Tuple[dict, str]]:
        """
        Возвращает итератор документов для ES.
        Записывает в стэйт дату последнего изменения, последней записи.
        """
        modified = ''
        for doc in docs:
            modified = doc.pop('modified')
            yield doc

        # Записываем в стейт только если у нас были какие-то записи
        if modified:
            self.state.set_state('modified', str(modified))

    @backoff(start_sleep_time=0.5)
    def bulk_update(self, docs: Iterator[dict], itersize: int,) -> None:
        """Загружает данные в ES используя итератор"""
        t = time.perf_counter()

        docs_generator = self.generate_docs(docs)
        lines, _ = helpers.bulk(
            client=self.elastic_connection,
            actions=docs_generator,
            index=self.index,
            chunk_size=itersize
        )

        elapsed_time = time.perf_counter() - t

        if lines == 0:
            logger.info("Nothing to update for index %s", self.index)
        else:
            logger.info(
                "%s lines saved in %s for index %s",
                lines, elapsed_time, self.index
            )
