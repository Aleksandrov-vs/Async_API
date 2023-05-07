import abc


class ElasticBaseStorage(abc.ABC):
    """Абстрактное хранилище данных elasticsearch."""

    @abc.abstractmethod
    def search(self, *args, **kwargs):
        """Поиск данных"""

    @abc.abstractmethod
    def get(self,*args, **kwargs):
        """Получить данные."""
    
    @abc.abstractmethod
    def close(self, *args, **kwargs):
        """Закрыть соединение."""


class RedisBaseStorage(abc.ABC):
    """Абстрактное хранилище данных redis."""
    
    @abc.abstractmethod
    def get(self, key):
        """Получить данные по ключу."""

    @abc.abstractmethod
    def set(self, key, value):
        """Установить данные по ключу со значением."""

    @abc.abstractmethod
    def close(self):
        """Закрыть соединение."""
