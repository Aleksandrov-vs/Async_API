import logging
import time
from datetime import datetime, MINYEAR, timezone

from redis import Redis

from settings import (
    app_config,
    elastic_config,
    logger_settings,
    postgres_dsn,
    redis_config
)
from extract import PostgresExtractor
from load import ElasticLoader
from state import State
from query import get_query


itersize = app_config.batch_size
freq = app_config.frequency
index = app_config.elastic_index

state = State(config=redis_config, redis_conn=Redis)
postgres_extractor = PostgresExtractor(dsn=postgres_dsn)
elastic_loader = ElasticLoader(config=elastic_config, state=state, index=index)
elastic_loader.create_index_if_not_exists()


def etl(query: str) -> None:
    """Загружает в elasticsearch данные пачками с помощью генераторов."""
    data_generator = postgres_extractor.extract_data(query, itersize)
    elastic_loader.bulk_update(data_generator, itersize)


if __name__ == '__main__':
    logging.basicConfig(**logger_settings)
    logger = logging.getLogger(__name__)

    while True:
        logger.info('Starting etl...')
        modified = state.get_state(
            'modified',
            default=str(datetime(MINYEAR, 1, 1, tzinfo=timezone.utc))
        )

        try:
            query = get_query(modified)
            etl(query)

        except ValueError as er:
            logger.error('Error: %s', er)
            continue

        logger.info('Sleep %s seconds...', freq)
        time.sleep(freq)
