import abc

from elasticsearch import NotFoundError
from pydantic import BaseModel

from db.base import RedisBaseStorage, ElasticBaseStorage
from services.redis_utils import key_generate


class Service(abc.ABC):
    @abc.abstractmethod
    def get_by_id(self, *args, **kwargs):
        """Получить данные по id"""
    
    @abc.abstractmethod
    def search(self, *args, **kwargs):
        """Поиск"""
    
    @abc.abstractmethod
    def get_data_from_elastic(self, *args, **kwargs):
        """Получить данные из elasticsearch"""
    
    @abc.abstractmethod
    def get_data_from_redis(self, *args, **kwargs):
        """Получить данные из redis"""


class BaseService(Service):
    def __init__(
            self,
            redis_storage: RedisBaseStorage,
            es_storage: ElasticBaseStorage
    ):
        self.redis_storage = redis_storage
        self.es_storage = es_storage
    
    async def search(
            self,
            index: str,
            body: dict,
            page_number: int | None,
            size: int | None,
            model: BaseModel,
            *args, **kwargs
    ) -> list:
        try:
            page = await self.es_storage.search(
                index=index,
                body=body,
                size=size,
                *args, **kwargs
            )
            hits = page['hits']['hits']
        except NotFoundError:
            return []
        pass

    async def get_data_from_elastic(self,
                                     index: str,
                                     uuid: str,
                                     model: BaseModel):
        try:
            doc = await self.es_storage.get(index, uuid)
        except NotFoundError:
            return None
        return model(**doc['_source'])

    async def get_data_from_redis(self,
                                   name_id: str,
                                   uuid: str,
                                   model: BaseModel):
        cache_data = await self.redis_storage.get(f'{name_id}:{uuid}')
        if not cache_data:
            return None

        data = model.parse_raw(cache_data)
        return data

    async def put_data_to_redis(self,
                                 name_id: str,
                                 data: BaseModel):
        await self.redis_storage.set(
                f'{name_id}:{data.id}',
                data.json(),
        )
