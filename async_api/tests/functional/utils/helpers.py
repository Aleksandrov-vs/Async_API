import json
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
logger.addHandler(handler)


async def get_es_bulk_query(
        es_data: list[dict],
        index: str
) -> list:
    bulk_query = []
    for i in index.split(', '):
        for row in es_data:
            bulk_query.extend([
                json.dumps({'index': {'_index': i, '_id': row['id']}}),
                json.dumps(row)
            ])

    return bulk_query
