from contextlib import closing
from dataclasses import asdict
from typing import Optional, Iterator

import psycopg2
from psycopg2.extensions import connection as pg_conn
from psycopg2.extras import DictCursor

from backoff_decorator import backoff
from schema import ESMovies, ESPersons, ESGenres
from settings import PostgresDSN


class PostgresExtractor:
    def __init__(
            self,
            dsn: PostgresDSN,
            postgres_connection: Optional[pg_conn] = None,
    ) -> None:
        self.dsn = dsn
        self.postgres_conn = postgres_connection

    @property
    def postgres_connection(self) -> pg_conn:
        """Создает новый объект сессии, если он не инициализирован или закрыт"""

        if self.postgres_conn is None or self.postgres_conn.closed:
            self.postgres_conn = self.create_connection()

        return self.postgres_conn

    @backoff()
    def create_connection(self) -> pg_conn:
        """Закрывает старый коннект и создает новый объект сессии"""
        if self.postgres_conn is not None:
            self.postgres_conn.close()

        return psycopg2.connect(**self.dsn.dict(), cursor_factory=DictCursor)

    @backoff()
    def extract_data(self, query: str, itersize: int, model: ESPersons | ESGenres | ESMovies) -> Iterator[dict]:
        """Выбирает пачку записей itersize и возвращает итератор данных."""
        with closing(self.postgres_connection) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                while user_chunk := cur.fetchmany(size=itersize):
                    for row in user_chunk:
                        instance = asdict(model(**row))
                        instance['_id'] = instance['id']
                        yield instance
