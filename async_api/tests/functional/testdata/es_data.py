import logging
import uuid
from random import choice, randint
genres = [{
    'id': str(uuid.uuid4()),
    'name': f'Genre_{val}'
} for val in range(10)]
print("жанры:", genres)

movies = [{
    'id': str(uuid.uuid4()),
    'imdb_rating': 8.5,
    'genre': [choice(genres)['name'] for _ in range(randint(1, 3))],
    'title': 'The Star',
    'description': 'New World',
    'director': [
        {'id': str(uuid.uuid4()), 'name': 'Ann'},
    ],
    'actors_names': ['Ann', 'Bob'],
    'writers_names': ['Ben', 'Howard'],
    'actors': [
        {'id': str(uuid.uuid4()), 'name': 'Ann'},
        {'id': str(uuid.uuid4()), 'name': 'Bob'}
    ],
    'writers': [
        {'id': str(uuid.uuid4()), 'name': 'Ben'},
        {'id': str(uuid.uuid4()), 'name': 'Howard'}
    ]
} for i in range(60)]


persons = [{
    'id': str(uuid.uuid4()),
    'full_name': "Person",
    'films': [
        {
            'id': str(uuid.uuid4()),
            'title': f'Film_{val}',
            'roles': [f'Film_{val}', ]},
    ],
} for val in range(60)]
