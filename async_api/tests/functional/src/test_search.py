import os
import sys
import logging
from http import HTTPStatus

import pytest

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import test_settings
from functional.testdata.es_data import movies

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'film_title': 'The Star', 'page_size': 60},
                {'status': HTTPStatus.OK, 'length': 60}
        ),
        (
                {'film_title': 'The Star', 'page_size': -50},
                {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 1}
        )
    ]
)
async def test_search_all_films(make_get_request, query_data: dict, expected_answer: dict):
    url = test_settings.service_url + '/api/v1/films/search/'
    body, status = await make_get_request(url, query_data)
    logging.info(status)

    assert status == expected_answer['status']

    if status == expected_answer['status']:
        assert len(body) == expected_answer['length'], \
            'The number of retrieved films does not match the expected length'

        if len(body) == HTTPStatus.OK:
            for film in movies:
                response_person = list(
                    filter(
                        lambda film_r: film_r['uuid'] == film['id'],
                        body
                    ))

                assert len(response_person) == 1, 'Multiple records with the same ID were returned or some ' \
                                                  'data is missing in the response body'
                assert response_person[0]['uuid'] == film['id']
                assert response_person[0]['title'] == film['title']

            cached_body, status = await make_get_request(url, query_data)

            assert cached_body == body
