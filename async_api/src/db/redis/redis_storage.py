from redis.asyncio import Redis
from db.redis import film, genre, person


redis: Redis | None = None


def on_startup(host: str, port: int):
    global redis
    redis = Redis(host=host, port=port)
    film.film_cache_repository = film.FilmCacheRepository(redis)
    genre.genre_cache_repository = genre.GenreCacheRepository(redis)
    person.person_cache_repository = person.PersonCacheRepository(redis)


def on_shutdown():
    redis.close()
