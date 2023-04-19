# Укажите необходимую версию python
FROM python:3.10

ENV PYTHONPATH "${PYTHONPATH}:/opt/"

# Выберите папку, в которой будут размещаться файлы проекта внутри контейнера
WORKDIR /opt/etl

# Заведите необходимые переменные окружения


# Скопируйте в контейнер файлы, которые редко меняются
COPY requirements.txt requirements.txt


# Установите зависимости
RUN  pip install --upgrade pip \
     && pip install -r requirements.txt --no-cache-dir


# Скопируйте всё оставшееся. Для ускорения сборки образа эту команду стоит разместить ближе к концу файла.
COPY . .


# Укажите, как запускать ваш сервис
CMD ["python", "main.py"]
