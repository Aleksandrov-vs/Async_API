import json

from redis.asyncio import Redis

from db.base import AbstractCacheStorage


CACHE_EXPIRE_IN_SECONDS = 60 * 5


class RedisStorage(AbstractCacheStorage):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def _get(self, key):
        return await self.redis.get(key)

    async def _set(self, key, value):
        await self.redis.set(
            key,
            value,
            expire=CACHE_EXPIRE_IN_SECONDS
        )

    def _key_generate(*args, **kwargs) -> str:
        return f'{args}:{json.dumps({"kwargs": kwargs}, sort_keys=True)}'

    async def close(self):
        self.redis.close()
        await self.redis.wait_closed()


redis_storage: AbstractCacheStorage | None = None


# Функция понадобится при внедрении зависимостей
async def get_redis_storage() -> AbstractCacheStorage:
    return redis_storage
