
import os, sys
import uuid
import json
import logging

import aiohttp
import pytest

from elasticsearch import AsyncElasticsearch

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import test_settings
from testdata.es_mapping import INDEX_MOVIES, INDEX_PERSONS, INDEX_GENRES


logger_settings = {
    'format': '%(asctime)s - %(name)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s',
    'datefmt': "%Y-%m-%d %H:%M:%S",
    'level': logging.INFO,
    'handlers': [logging.StreamHandler()],
}
logging.basicConfig(**logger_settings)
logger = logging.getLogger(__name__)

#  Название теста должно начинаться со слова `test_`
#  Любой тест с асинхронными вызовами нужно оборачивать декоратором `pytest.mark.asyncio`, который следит за запуском и работой цикла событий. 

@pytest.mark.asyncio
async def test_search():

    # 1. Генерируем данные для ES

    es_data = [{
        'id': str(uuid.uuid4()),
        'imdb_rating': 8.5,
        'genre': ['Action', 'Sci-Fi'],
        'title': 'The Star',
        'description': 'New World',
        'director': [
            {'id': '111', 'name': 'Ann'},
        ],
        'actors_names': ['Ann', 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        'actors': [
            {'id': '111', 'name': 'Ann'},
            {'id': '222', 'name': 'Bob'}
        ],
        'writers': [
            {'id': '333', 'name': 'Ben'},
            {'id': '444', 'name': 'Howard'}
        ],
        # 'created_at': datetime.datetime.now().isoformat(),
        # 'updated_at': datetime.datetime.now().isoformat(),
        # 'film_work_type': 'movie'
    } for _ in range(60)]
     
    bulk_query = []
    for row in es_data:
        # print(row)
        bulk_query.extend([
            json.dumps({'index': {'_index': 'movies', '_id': row['id']}}),
            json.dumps(row)
        ])

    str_query = '\n'.join(bulk_query) + '\n'

    # 2. Загружаем данные в ES

    es_client = AsyncElasticsearch(hosts=f'{test_settings.es_host}:{test_settings.es_port}', 
                                   validate_cert=False, 
                                   use_ssl=False)
    # await es_client.indices.flush(index='movies')
    if not await es_client.indices.exists('movies'):
        await es_client.indices.create(index='movies', body=INDEX_MOVIES)
    response = await es_client.bulk(
        str_query,
        refresh=True)
    await es_client.close()
    if response['errors']:
        raise Exception('Ошибка записи данных в Elasticsearch')
    
    # 3. Запрашиваем данные из ES по API

    url = test_settings.service_url + '/api/v1/films/search'
    query_data = {'search': 'The Star'}
    session = aiohttp.ClientSession()
    async with session.get(url, params=query_data) as response:
        logger.info(await response.json())
        body = await response.json()
        headers = response.headers
        status = response.status
    await session.close()

    # 4. Проверяем ответ 

    assert status == 200
    assert len(body) == 50
