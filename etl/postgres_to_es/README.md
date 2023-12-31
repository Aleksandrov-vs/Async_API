# Проектное задание: ETL

Написать отказоустойчивый перенос данных из PostgreSQL в Elasticsearch

## Пригцип работы
- backoff_decorator.py - функция для повторного выполнения функции через некоторое время, если возникла ошибка
- es_index.py - тут индекс с настройками, для создания схемы в ES
- extract.py - работа с PG, читает из БД записи пачками, равными BATCH_SIZE в .env
- load.py - работа с ES, записывает данные пачками равными BATCH_SIZE в .env
- main.py - тут происходит запуск всего приложения
- query.py - запрос в PG, который выбирает всю информацию
- schema.py - датаклассы необходимые для работы ETL модуля
- settings.py - классы конфигурации с валидацией pydantic
- state.py - хранит состояние по дате последнего обновления в redis

Так же есть postman_tests.json, для тестирования результата работы etl

## Dev:

Необходимо создать .env файл на основе .env.example

## Запуск приложения в Docker

```
$ docker-compose up --build -d
```

## Остановка приложения

```
$ docker-compose stop или docker-compose down
```
