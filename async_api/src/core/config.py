import os
from logging import config as logging_config
from pydantic import BaseSettings, Field
from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    project_name: str = Field('movies', env='PROJECT_NAME')
    redis_host: str = Field('localhost', env='REDIS_HOST')
    redis_port: int = Field(6379, env='REDIS_PORT')
    elastic_host: str = Field('localhost', env='ELASTICSEARCH_HOST')
    elastic_port: int = Field(9200, env='ELASTICSEARCH_PORT')
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# # Название проекта. Используется в Swagger-документации
# PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')
#
# # Настройки Redis
# REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
# REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
#
# # Настройки Elasticsearch
# ELASTIC_HOST = os.getenv('ELASTICSEARCH_HOST', '127.0.0.1')
# ELASTIC_PORT = int(os.getenv('ELASTICSEARCH_PORT', 9200))
#
# # Корень проекта
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
