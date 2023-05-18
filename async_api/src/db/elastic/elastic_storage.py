from elasticsearch import AsyncElasticsearch

from db.elastic import film, person
from db.elastic import genre


es: AsyncElasticsearch | None = None


def on_startup(data_storage_hosts: list):
    global es
    es = AsyncElasticsearch(hosts=data_storage_hosts)
    film.film_repository = film.FilmElasticRepository(es)
    genre.genre_repository = genre.GenreElasticRepository(es)
    person.person_repository = person.PersonElasticRepository(es)


def on_shutdown():
    es.close()

