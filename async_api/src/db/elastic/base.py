import logging
from uuid import UUID
from pydantic import BaseModel
from typing import Type, List, Union

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError, RequestError

from db.base import AbstractDataStorage


class BaseElasticStorage(AbstractDataStorage):
    def __init__(self, elastic: AsyncElasticsearch) -> None:
        self.elastic = elastic

    async def _get_by_id(
            self,
            index: str,
            obj_id: UUID,
            response_model: Type[BaseModel] | None
    ) -> Union[BaseModel, List] | None:
        """Получить данные."""
        try:
            doc = await self.elastic.get(index, obj_id)
        except NotFoundError:
            return None
        logging.info(f'response model is: {response_model}')
        logging.info(f'doc  is: {doc}')
        if response_model is None:
            return doc
        return response_model(**doc['_source'])

    async def _search(
            self,
            index: str,
            body_of_query: dict,
            page_number: int | None = None,
            size: int | None = None,
            *args, **kwargs
    ) -> list:
        try:
            from_ = size * (page_number - 1) if page_number is not None else None
            page = await self.elastic.search(
                index=index,
                body=body_of_query,
                size=size,
                from_=from_,
                *args, **kwargs
            )
            hits = page['hits']['hits']
            return hits
        except NotFoundError:
            return []
        except RequestError:
            return []

    async def close(self):
        await self.elastic.close()


elastic_storage: BaseElasticStorage | None = None
