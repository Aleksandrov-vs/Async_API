from Async_API_sprint_1.async_api.src.db import elastic_storage
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.v1 import films, genres, persons
from core.config import settings
from Async_API_sprint_1.async_api.src.db import redis_storage

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    redis_storage.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    elastic_storage.es = AsyncElasticsearch(
        hosts=[f'{settings.elastic_host}:{settings.elastic_port}']
    )


@app.on_event('shutdown')
async def shutdown():
    await redis_storage.redis.close()
    await elastic_storage.es.close()


# Подключаем роутер к серверу, указав префикс /v1/films
# Теги указываем для удобства навигации по документации
app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons'])
