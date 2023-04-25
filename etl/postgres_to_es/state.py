import logging

import redis
from redis import Redis

from settings import RedisConfig
from backoff_decorator import backoff


logger = logging.getLogger(__name__)


def is_redis_available(redis_conn: Redis) -> bool:
    try:
        redis_conn.ping()
    except Exception:
        return False
    return True


class State:
    """Класс для работы с состояниями."""

    def __init__(
            self,
            config: RedisConfig,
            redis_conn: Redis | None
    ) -> None:
        self.config = config
        self.redis_conn = redis_conn

    @property
    def redis_connection(self) -> Redis:
        """Использует текущее соединение или создает новое"""
        try:
            if not self.redis_conn or not is_redis_available(self.redis_conn):
                self.redis_conn = self.create_connection()
        except redis.exceptions.ConnectionError as er:
            logger.error('Redis connection refused: ', er)
            return
        return self.redis_conn

    @backoff()
    def create_connection(self) -> Redis:
        """Создает новое соединение к Redis"""
        return Redis(**self.config.dict())

    @backoff()
    def set_state(self, key: str, value: str) -> None:
        """Установить состояние для определённого ключа."""
        self.redis_connection.set(key, value.encode())

    @backoff()
    def get_state(self, key: str, default: str | None) -> str:
        """Получить состояние по определённому ключу."""
        state = self.redis_connection.get(key)
        if state:
            return state.decode()
        return default
