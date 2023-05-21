import os, sys
import pytest


current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import test_settings


pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    'expected_answer',
    [
        (
                {'status': 200, 'length': 10}
        ),
    ]
)
async def test_genre_search(
    make_get_request,
    expected_answer: dict
):
    url = test_settings.service_url + '/api/v1/genres/'
    body, status = await make_get_request(url)

    assert len(body) == expected_answer['length']
    assert status == expected_answer['status']
