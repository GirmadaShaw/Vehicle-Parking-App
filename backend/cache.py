from backend import redis_client
import json

def cache_get(key):
    value = redis_client.get(key)
    return json.loads(value) if value else None

def cache_set(key, data, ttl=60):
    redis_client.setex(key, ttl, json.dumps(data))

def cache_delete(key):
    redis_client.delete(key)
