from contextlib import contextmanager
from typing import Iterator

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from etl.config.settings import BACKOFF_CONFIG
from etl.utils.backoff import backoff


@contextmanager
@backoff(**BACKOFF_CONFIG, mode='gen')
def conn_context_postgresql(dsl: dict) -> Iterator[_connection]:
    """ Контекстный менеджер для postgres """
    conn_postgres = psycopg2.connect(**dsl, cursor_factory=DictCursor)
    yield conn_postgres
    conn_postgres.commit()
    conn_postgres.close()
