import os
import sys
import time

from elasticsearch import Elasticsearch

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import test_settings

if __name__ == '__main__':
    es_client = Elasticsearch(
        hosts=f'{test_settings.es_host}:{test_settings.es_port}',
        validate_cert=False,
        use_ssl=False
    )
    while True:
        if es_client.ping():
            break
        time.sleep(1)
