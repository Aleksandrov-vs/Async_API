import os
from logging import config as logging_config

from pydantic import BaseSettings, Field

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    project_name: str = Field('movies', env='PROJECT_NAME')
    redis_host: str = Field('localhost', env='REDIS_HOST')
    redis_port: int = Field(6379, env='REDIS_PORT')
    elastic_host: str = Field('localhost', env='ELASTICSEARCH_HOST')
    elastic_port: int = Field(9200, env='ELASTICSEARCH_PORT')
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


settings = Settings()
