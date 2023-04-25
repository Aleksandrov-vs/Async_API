FROM python:3.10-alpine

WORKDIR /etl

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt --no-cache-dir

COPY ./ .

RUN addgroup --gid 1001 --system app \
    && adduser --no-create-home \
    --shell /bin/false --disabled-password \
    --uid 1001 --system app \
    && chown -R app:app /etl

USER app

ENTRYPOINT ["sh", "docker-entrypoint.sh"]
