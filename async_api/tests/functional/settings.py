from pydantic import BaseSettings, Field
from dotenv import load_dotenv


load_dotenv()


class TestSettings(BaseSettings):
    es_host: str = Field('localhost', env='ELASTICSEARCH_HOST')
    es_port: int = Field(9200, env='ELASTICSEARCH_PORT')
    es_index: str = 'movies, genres, persons'

    redis_host: str = Field('localhost', env='REDIS_HOST')
    redis_port: int = Field(6379, env='REDIS_PORT')

    service_url: str = Field('http://127.0.0.1:8000', env='SERVICE_URL')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

test_settings = TestSettings()
