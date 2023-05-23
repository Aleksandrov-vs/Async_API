import logging
import os
import sys

import pytest

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import test_settings
from functional.testdata.es_data import movies
from http import HTTPStatus

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'page_size': 60},
                {'status': HTTPStatus.OK, 'length': 60}
        )
    ]
)
async def test_get_all_films(make_get_request, query_data: dict, expected_answer: dict):
    url = test_settings.service_url + '/api/v1/films/'
    body, status = await make_get_request(url, query_data)
    assert len(body) == expected_answer['length'], 'The number of retrieved films does not match the expected length'
    assert status == expected_answer['status']

    if len(body) == expected_answer['length']:
        for film in movies:
            response_film = list(
                filter(
                    lambda film_r: film_r['uuid'] == film['id'],
                    body
                ))
            assert len(response_film) == 1, 'Multiple records with the same ID were returned or some ' \
                                            'data is missing in the response body'
            assert response_film[0]['uuid'] == film['id']
            assert response_film[0]['title'] == film['title']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'film': movies[0]},
                {'status': HTTPStatus.OK}
        ),
        (
                {'film': movies[5]},
                {'status': HTTPStatus.OK}
        ),
        (
                {'film': {'id': "123", 'title': "NonExisting"}},
                {'status': HTTPStatus.NOT_FOUND}
        )
    ]
)
async def test_get_film_by_id(make_get_request, expected_answer: dict, query_data: dict):
    film = query_data['film']
    url = test_settings.service_url + f'/api/v1/films/{film["id"]}'
    body, status = await make_get_request(url)
    logging.info(status)
    assert status == expected_answer['status']
    if status == HTTPStatus.OK:
        assert film['id'] == body['uuid']
        assert film['title'] == body['title']
    cache_body, status = await make_get_request(url)
    if status == HTTPStatus.OK:
        assert cache_body == body
