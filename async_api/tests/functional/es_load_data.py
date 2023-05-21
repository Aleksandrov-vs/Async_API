import asyncio
import aiohttp
import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch

from functional.testdata.es_mapping import INDEX_MOVIES, INDEX_PERSONS, INDEX_GENRES
from functional.testdata import es_data
from functional.utils.helpers import get_es_bulk_query


@pytest.fixture(scope='session')
def es_write_data(es_client: AsyncElasticsearch):
    async def inner(data: list[dict], index_name):
        bulk_query = await get_es_bulk_query(
            data,
            index_name,
        )
        str_query = '\n'.join(bulk_query) + '\n'

        response = await es_client.bulk(str_query, refresh=True)
        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')
    return inner


@pytest_asyncio.fixture(scope='session')
async def es_create_indexes(es_client: AsyncElasticsearch):
    async def inner():
        print('создание индексов')
        await es_client.indices.delete(index='movies', ignore=[400, 404])
        await es_client.indices.create(
            index='movies',
            body=INDEX_MOVIES,
        )

        await es_client.indices.delete(index='genres', ignore=[400, 404])
        await es_client.indices.create(
            index='genres',
            body=INDEX_GENRES,
        )

        await es_client.indices.delete(index='persons', ignore=[400, 404])
        await es_client.indices.create(
            index='persons',
            body=INDEX_PERSONS,
        )
        print('индексы созданы')
    return inner


@pytest_asyncio.fixture(scope='session', autouse=True)
async def create_data(es_write_data,  es_create_indexes):
    await es_create_indexes()
    print('создание данных')
    await es_write_data(es_data.movies, "movies")
    await es_write_data(es_data.persons, "persons")
    await es_write_data(es_data.genres, "genres")
    print('данные загружены')