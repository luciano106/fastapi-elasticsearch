import time

from elasticsearch import Elasticsearch
from app.config import ELASTICSEARCH_URL
from redis import asyncio as aioredis
from app.config import REDIS_URL

# Retries to wait for Elasticsearch to become available
for _ in range(10):
    try:
        es = Elasticsearch([ELASTICSEARCH_URL])
        if es.ping():
            break
    except Exception as e:
        time.sleep(5)
else:
    raise ValueError("Failed to connect to Elasticsearch")

# Get redis client
redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)