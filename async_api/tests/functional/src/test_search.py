import os, sys
import pytest


current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import test_settings


pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'film_title': 'The Star'},
                {'status': 200, 'length': 50}
        ),
    ]
)
async def test_film_search(
    make_get_request,
    query_data: dict,
    expected_answer: dict
):
    url = test_settings.service_url + '/api/v1/films/search/'
    body, status = await make_get_request(url, query_data)

    assert len(body) == expected_answer['length']
    assert status == expected_answer['status']
