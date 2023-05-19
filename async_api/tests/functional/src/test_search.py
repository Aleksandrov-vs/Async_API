import os, sys
import pytest


current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import test_settings
from testdata.es_data import get_es_data


pytestmark = pytest.mark.asyncio

@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'search': 'The Star'},
                {'status': 200, 'length': 50}
        ),
        # (
        #         {'search': 'Mashed potato'},
        #         {'status': 200, 'length': 0}
        # )
    ]
)
async def test_search(
    es_write_data,
    make_get_request,
    query_data: dict,
    expected_answer: dict
):
    await es_write_data(get_es_data())
    url = test_settings.service_url + '/api/v1/films/search'
    body, status = await make_get_request(url, query_data)

    assert len(body) == expected_answer['length']
    assert status == expected_answer['status']
