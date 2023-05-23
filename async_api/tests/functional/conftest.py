import asyncio
import aiohttp
import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch

from functional.settings import test_settings

pytest_plugins = [
   "functional.es_load_data",
]


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


@pytest_asyncio.fixture(scope='function')
async def session_client():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope='function')
def make_get_request(session_client: aiohttp.ClientSession):
    async def inner(url: str, params: dict = None):
        async with session_client.get(url, params=params) as response:
            body = await response.json()
            status = response.status
            print(body)
            return body, status

    return inner
