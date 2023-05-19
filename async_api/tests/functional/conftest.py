import os, sys
import asyncio
import aiohttp
import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch

from functional.settings import test_settings
from functional.testdata.es_mapping import INDEX_MOVIES, INDEX_PERSONS, INDEX_GENRES
from functional.utils.helpers import get_es_bulk_query


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def es_client():
    client = AsyncElasticsearch(
        hosts=f'{test_settings.es_host}:{test_settings.es_port}', 
        validate_cert=False, 
        use_ssl=False)
    yield client
    await client.close()


@pytest.fixture(scope="session")
async def es_create_index(es_client: AsyncElasticsearch):
    await es_client.indices.create(
        index='movies',
        body=INDEX_MOVIES,
    )


@pytest_asyncio.fixture(scope='function')
async def session_client():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope='session')
def es_write_data(es_client: AsyncElasticsearch):
    async def inner(data: list[dict]):
        bulk_query = await get_es_bulk_query(
            data,
            test_settings.es_index,
        )
        str_query = '\n'.join(bulk_query) + '\n'

        response = await es_client.bulk(str_query, refresh=True)
        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')
    return inner 


@pytest.fixture(scope='function')
def make_get_request(session_client: aiohttp.ClientSession):
    async def inner(url: str, data: dict):
        async with session_client.get(url, params=data) as response:
            body = await response.json()
            status = response.status
            print(body)
            return body, status

    return inner
