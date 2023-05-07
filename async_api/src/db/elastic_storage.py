from uuid import UUID
from base import ElasticBaseStorage
from elasticsearch import AsyncElasticsearch


class ElasticStorage(ElasticBaseStorage):
    def __init__(self, elastic: AsyncElasticsearch) -> None:
        self.elastic = AsyncElasticsearch(hosts=elastic)

    async def get(self, *args, **kwargs):
        return await self.elastic.get(*args, **kwargs)

    async def search(self, *args, **kwargs):
        return await self.elastic.search(*args, **kwargs)

    async def close(self):
        await self.elastic.close()


es: ElasticBaseStorage | None = None


# Функция понадобится при внедрении зависимостей
async def get_elastic() -> ElasticBaseStorage:
    return es
