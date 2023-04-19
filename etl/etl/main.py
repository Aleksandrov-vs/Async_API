from time import sleep

from etl.config.settings import STATE_PATH, DATABASES, EXTRACT_CONFIG, ELASTIC_CONFIG, SLEEP_TIME
from etl.extract.pg_extractor import PostgresExtractor
from etl.load.elastic_loader import ElasticLoader
from etl.transform.es_data import TransformETL
from etl.utils.elastic_conn import conn_context_elasticsearch
from etl.utils.pg_conn import conn_context_postgresql
from etl.utils.state import JsonFileStorage, State

storage = JsonFileStorage(STATE_PATH)
state = State(storage)

if __name__ == "__main__":
    with conn_context_postgresql(DATABASES['postgres']) as conn_pg, \
            conn_context_elasticsearch(host=ELASTIC_CONFIG['host'], port=ELASTIC_CONFIG['port']) as conn_es:
        while True:
            pg_extract = PostgresExtractor(conn_pg, state)
            data = pg_extract.get_data(EXTRACT_CONFIG)
            transform = TransformETL(data).transform_data()
            es_loader = ElasticLoader(conn_es, transform, ELASTIC_CONFIG, state)
            es_loader.upload_data()
            sleep(SLEEP_TIME)
