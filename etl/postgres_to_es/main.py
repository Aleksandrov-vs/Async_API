import logging
import time
from datetime import datetime, MINYEAR, timezone

from redis import Redis

from extract import PostgresExtractor
from es_index import INDEX_MOVIES, INDEX_GENRES, INDEX_PERSONS
from load import ElasticLoader
from query import get_query
from schema import ESMovies, ESPersons, ESGenres
from settings import (
    app_config,
    elastic_config,
    logger_settings,
    postgres_dsn,
    redis_config
)
from state import State

itersize = app_config.batch_size
freq = app_config.frequency
movies_index = app_config.movies_index
persons_index = app_config.persons_index
genres_index = app_config.genres_index

state = State(config=redis_config, redis_conn=Redis)
postgres_extractor = PostgresExtractor(dsn=postgres_dsn)
movies_loader = ElasticLoader(config=elastic_config, state=state, index=movies_index, state_key='movies_modified')
persons_loader = ElasticLoader(config=elastic_config, state=state, index=persons_index, state_key='persons_modified')
genres_loader = ElasticLoader(config=elastic_config, state=state, index=genres_index, state_key='genres_modified')

loaders = {
    movies_loader: ('movies', ESMovies, INDEX_MOVIES),
    persons_loader: ('persons', ESPersons, INDEX_PERSONS),
    genres_loader: ('genres', ESGenres, INDEX_GENRES)
}

for loader in loaders:
    loader.create_index_if_not_exists(loaders[loader][2])


def etl(query: str, loader: ElasticLoader) -> None:
    """Загружает в elasticsearch данные пачками с помощью генераторов."""
    data_generator = postgres_extractor.extract_data(query, itersize, loaders[loader][1])
    loader.bulk_update(data_generator, itersize)


if __name__ == '__main__':
    logging.basicConfig(**logger_settings)
    logger = logging.getLogger(__name__)
    logger.info('Starting etl...')
    while True:
        for loader in loaders:
            logger.info(f'{loaders[loader][0]} is loading...')
            modified = state.get_state(
                loader.state_key,
                default=str(datetime(MINYEAR, 1, 1, tzinfo=timezone.utc))
            )

            try:
                query = get_query(modified, loaders[loader][0])
                etl(query, loader)
            except ValueError as er:
                logger.error('Error: %s', er)
                continue

        logger.info('Sleep %s seconds...', freq)
        time.sleep(freq)
