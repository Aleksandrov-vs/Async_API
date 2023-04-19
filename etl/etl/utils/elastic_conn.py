from contextlib import contextmanager
from typing import Iterator

from elasticsearch import Elasticsearch

from etl.config.settings import BACKOFF_CONFIG
from etl.utils.backoff import backoff


@contextmanager
@backoff(**BACKOFF_CONFIG, mode='gen')
def conn_context_elasticsearch(host: str, port: int) -> Iterator[Elasticsearch]:
    """ Контекстный менеджер для elasticsearch """
    es = Elasticsearch([{'scheme': 'http', 'host': host, 'port': port}])
    if es.ping():
        yield es
    else:
        raise ConnectionError('Failed to connect elasticsearch')
    es.close()
