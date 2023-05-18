import abc
from pydantic import BaseModel
from typing import Type, Union
from uuid import UUID


class AbstractDataStorage(abc.ABC):
    """Абстрактное хранилище данных elasticsearch."""

    @abc.abstractmethod
    async def _search(
        self,
        index: str,
        body_of_query: dict,
        page_number: int | None,
        size: int | None,
        *args, **kwargs
    ) -> list:
        """Поиск данных"""

    @abc.abstractmethod
    async def _get_by_id(
            self,
            index: str,
            obj_id: UUID,
            response_model: Type[BaseModel] | None
    ) -> Union[BaseModel, list] | None:
        """Получить данные."""
    
    @abc.abstractmethod
    def close(self, *args, **kwargs):
        """Закрыть соединение."""


class AbstractCacheStorage(abc.ABC):
    """Абстрактное хранилище данных redis."""
    
    @abc.abstractmethod
    def _get(self, key):
        """Получить данные по ключу."""

    @abc.abstractmethod
    def _set(self, key, value):
        """Установить данные по ключу со значением."""

    def _key_generate(*args, **kwargs) -> str:
        """Генерация ключа для хранения в кеш"""

    @abc.abstractmethod
    def close(self):
        """Закрыть соединение."""
