# redis
import redis
from configs.auth import REDIS_DB, REDIS_PORT, REDIS_HOST
redis_instance = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# mongodb
from pymongo import MongoClient
from configs.auth import MONGODB_PORT, MONGODB_HOST, MONGODB_NAME
db_client = MongoClient(MONGODB_HOST, MONGODB_PORT)
db_instance = db_client[MONGODB_NAME]

# elastic search
from elasticsearch import Elasticsearch
es_instance = Elasticsearch()

