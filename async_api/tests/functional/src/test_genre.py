import logging
import os
import sys
from http import HTTPStatus

import pytest

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import test_settings
from functional.testdata.es_data import genres


pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    'expected_answer',
    [
        (
                {'status': HTTPStatus.OK, 'length': 10}
        ),
    ]
)
async def test_get_all_genres(
    make_get_request,
    expected_answer: dict
):
    url = test_settings.service_url + '/api/v1/genres/'
    body, status = await make_get_request(url)

    assert len(body) == expected_answer['length'], 'количество записанных и ' \
                                                   'полученных данных не совпадает'
    assert status == expected_answer['status']

    if len(body) == expected_answer['length']:
        for genre in genres:
            response_genre = list(
                filter(
                    lambda genre_r: genre_r['uuid'] == genre['id'],
                    body
                ))
            assert len(response_genre) == 1, 'вернулось несколько записей' \
                                             ' с одинаковыми id или часть ' \
                                             'данных нет в теле запроса'
            assert response_genre[0]['uuid'] == genre['id']
            assert response_genre[0]['name'] == genre['name']


@pytest.mark.parametrize(
     'query_data, expected_answer',
    [
        (
            {'genre': genres[0]},
            {'status': HTTPStatus.OK}
        ),
        (
            {'genre': genres[5]},
            {'status': HTTPStatus.OK}
        ),
        (
                {
                    'genre': {
                        'id': "123",
                        'name': "wer"
                    }
                },
                {'status': HTTPStatus.UNPROCESSABLE_ENTITY}
        )
    ]
)
async def test_get_genre_by_id(
    make_get_request,
    expected_answer: dict,
    query_data: dict,
):
    genre = query_data['genre']
    url = test_settings.service_url + f'/api/v1/genres/{genre["id"]}'
    body, status = await make_get_request(url)
    logging.info(status)
    assert status == expected_answer['status']
    if status == HTTPStatus.OK:
        assert genre['id'] == body['uuid']
        assert genre['name'] == body['name']
