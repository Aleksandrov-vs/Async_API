import logging
import os
import sys
import uuid

import pytest

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import test_settings
from functional.testdata.es_data import persons
from http import HTTPStatus

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'person': persons[0]},
                {'status': HTTPStatus.OK}
        ),
        (
                {'person': persons[5]},
                {'status': HTTPStatus.OK}
        ),
        (
                {'person': {'id': str(uuid.uuid4()), 'full_name': "NonExisting"}},
                {'status': HTTPStatus.NOT_FOUND}
        )
    ]
)
async def test_get_person_by_id(make_get_request, expected_answer: dict, query_data: dict):
    person = query_data['person']
    url = test_settings.service_url + f'/api/v1/persons/{person["id"]}'
    body, status = await make_get_request(url)
    logging.info(status)
    assert status == expected_answer['status']
    if status == HTTPStatus.OK:
        assert person['id'] == body['uuid']
        assert person['full_name'] == body['full_name']
    cache_body, status = await make_get_request(url)
    if status == HTTPStatus.OK:
        assert cache_body == body


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'person': persons[1]},
                {'status': HTTPStatus.OK}
        ),
        (
                {'person': persons[3]},
                {'status': HTTPStatus.OK}
        ),
        (
                {'person': {'id': str(uuid.uuid4()), 'full_name': "NonExisting"}},
                {'status': HTTPStatus.NOT_FOUND}
        )
    ]
)
async def test_get_person_films_by_id(make_get_request, expected_answer: dict, query_data: dict):
    person = query_data['person']
    url = test_settings.service_url + f'/api/v1/persons/{person["id"]}/film'
    body, status = await make_get_request(url)
    logging.info(status)
    assert status == expected_answer['status']
    if status == HTTPStatus.OK:
        assert person['films'][0]['id'] == body[0]['uuid']
    cache_body, status = await make_get_request(url)
    if status == HTTPStatus.OK:
        assert cache_body == body


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'person_name': 'Vasya', 'page_size': 60},
                {'status': HTTPStatus.OK, 'length': 60}
        ),
        (
                {'person_name': 'Vasya', 'page_size': -50},
                {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 1}
        )
    ]
)
async def test_search_all_person(make_get_request, query_data: dict, expected_answer: dict):
    url = test_settings.service_url + '/api/v1/persons/search/'
    body, status = await make_get_request(url, query_data)
    assert status == expected_answer['status']
    if status == expected_answer['status']:
        assert len(body) == expected_answer['length'], \
            'The number of retrieved films does not match the expected length'
        if len(body) == HTTPStatus.OK:
            for person in persons:
                response_person = list(
                    filter(
                        lambda person_r: person_r['uuid'] == person['id'],
                        body
                    ))
                assert len(response_person) == 1, 'Multiple records with the same ID were returned or some ' \
                                                  'data is missing in the response body'
                assert response_person[0]['uuid'] == person['id']
                assert response_person[0]['full_name'] == person['full_name']
