import logging
import uuid


movies = [{
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
    ]
} for _ in range(60)]


persons = [{
    'id': str(uuid.uuid4()),
    'full_name': f"vasya {val}",
    'films': [
        {
            'id': str(uuid.uuid4()),
            'title': f'Film_{val}',
            'roles': [f'Film_{val}', ]},
    ],
} for val in range(60)]

genres = [{
    'id': str(uuid.uuid4()),
    'name': f'Genre_{val}'
} for val in range(60)]

