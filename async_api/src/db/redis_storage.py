from redis.asyncio import Redis

from base import RedisBaseStorage


FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class RedisStorage(RedisBaseStorage):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key):
        return await self.redis.get(key)

    async def set(self, key, value):
        await self.redis.set(
            key,
            value,
            expire=FILM_CACHE_EXPIRE_IN_SECONDS
        )

    async def close(self):
        self.redis.close()
        await self.redis.wait_closed()


redis: RedisBaseStorage | None = None

# Функция понадобится при внедрении зависимостей
async def get_redis() -> RedisBaseStorage:
    return redis
