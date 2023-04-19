import logging

from pydantic import BaseSettings, Field

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('app.log'), logging.StreamHandler()]
)


class PostgresConfig(BaseSettings):
    dbname: str = Field(..., env="POSTGRES_DB")
    user: str = Field(..., env="POSTGRES_USER")
    password: str = Field(..., env="POSTGRES_PASSWORD")
    host: str = Field("localhost", env="DB_HOST")
    port: int = Field(5432, env="POSTGRES_PORT")


class AppConfig(BaseSettings):
    state_path: str = Field('state.json', env="STATE_PATH")
    sleep_time: int = Field(10, env="SLEEP_TIME")


class EsConfig(BaseSettings):
    host: str = Field('localhost', env="ELASTIC_HOST")
    port: int = Field(9200, env="ELASTIC_PORT")
    index: str = Field('movies', env="ELASTIC_INDEX")
    batch: int = Field(1000, env="ELASTIC_BATCH")
    index_path: str = Field('es_index.json', env="INDEX_PATH")


class BackoffConfig(BaseSettings):
    start_sleep_time: float = Field(0.1, env="BACKOFF_START_TIME")
    factor: int = Field(2, env="BACKOFF_FACTOR")
    border_sleep_time: int = Field(10, env="BACKOFF_BORDER_TIME")


class ExtractorEnricher(BaseSettings):
    batch_size: int = Field(1000, env="POSTGRES_BATCH")
    db_schema: str = Field('content', env="POSTGRES_SCHEMA", alias='schema')


class ExtractorProducer(BaseSettings):
    db_schema: str = Field('content', env="POSTGRES_SCHEMA", alias='schema')
    table: str
    state_key: str


class ExtractorMerger(ExtractorEnricher):
    batch_size: int = Field(1000, env="POSTGRES_BATCH")
    base_table: str
    base_table_id: str
    merge_table: str
    merge_table_id: str
    merge_table_fk: str


class PersonsExtractor(BaseSettings):
    producer: ExtractorProducer = ExtractorProducer(table='person', state_key='persons_modified')
    merger: ExtractorMerger = ExtractorMerger(base_table='film_work', base_table_id='id',
                                              merge_table='person_film_work', merge_table_id='person_id',
                                              merge_table_fk='film_work_id')
    enricher: ExtractorEnricher = ExtractorEnricher()


class GenresExtractor(BaseSettings):
    producer: ExtractorProducer = ExtractorProducer(table='genre', state_key='genres_modified')
    merger: ExtractorMerger = ExtractorMerger(base_table='film_work', base_table_id='id', merge_table='genre_film_work',
                                              merge_table_id='genre_id', merge_table_fk='film_work_id')
    enricher: ExtractorEnricher = ExtractorEnricher()


class FilmsExtractor(BaseSettings):
    producer: ExtractorProducer = ExtractorProducer(table='film_work', state_key='films_modified')
    enricher: ExtractorEnricher = ExtractorEnricher()


class ExtractorConfig(BaseSettings):
    persons: PersonsExtractor = PersonsExtractor()
    genres: GenresExtractor = GenresExtractor()
    films: FilmsExtractor = FilmsExtractor()


DATABASES = {
    'postgres': PostgresConfig().dict()
}

BACKOFF_CONFIG = BackoffConfig().dict()

STATE_PATH = AppConfig().state_path

SLEEP_TIME = AppConfig().sleep_time

BATCH_SIZE = ExtractorEnricher().batch_size

ELASTIC_CONFIG = EsConfig().dict()

EXTRACT_CONFIG = ExtractorConfig().dict()
