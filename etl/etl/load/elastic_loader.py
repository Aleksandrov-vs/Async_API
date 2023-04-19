import json
import logging
from dataclasses import asdict
from typing import Dict, Union, Iterable, Any

from elasticsearch import Elasticsearch, helpers
from more_itertools import ichunked

from etl.transform.models import Movie
from etl.utils.state import State


class ElasticLoader:
    """ Класс для загрузки данных в elasticsearch """

    def __init__(self, conn: Elasticsearch, data: Iterable[Movie], config: Dict[str, Union[str, int]],
                 state: State) -> None:
        """
        Инициализация класса
        :param conn: Подлкючение к базе elasticsearch
        :param data: Данные для загрузки
        :param config: Конфиг
        :param state: Объект класса состояния
        """
        self.conn = conn
        self.config = config
        self.data = data
        self.state = state
        self.index_settings = None

    def create_index(self) -> None:
        """
        Функция создания схемы, если ее еще нет
        """
        if not self.index_settings:
            with open(self.config['index_path'], 'r') as f:
                self.index_settings = json.load(f)
            self.conn.indices.create(index=self.config['index'], body=self.index_settings, ignore=400)

    def generate_doc(self) -> Dict[str, Any]:
        """
        Функция создания документов для загрузки в elastic
        :return: Строки в формате словарей
        """
        for elem in self.data:
            doc = asdict(elem)
            doc['_id'] = doc['id']
            yield doc

    def upload_data(self) -> None:
        """
        Функция загрузки данных в elastic
        """
        self.create_index()
        docs = self.generate_doc()
        for chunk in ichunked(docs, self.config['batch']):
            lines, _ = helpers.bulk(client=self.conn, index=self.config['index'], actions=chunk, raise_on_error=False)
            if lines != 0:
                logging.info(f'{lines} are uploaded to index {self.config["index"]}')
            else:
                logging.error('Error while uploading data...')
