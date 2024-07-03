import json
from typing import Dict, Any
from functools import wraps
from core.cache import redis_client, cache_key
from core.database import get_db
from models.cache_item import CacheItem

async def cache_data(key: str, data: Dict[str, Any]):
    redis_client.set(key, json.dumps(data))
    db = next(get_db())
    db_item = CacheItem(key=key, value=json.dumps(data))
    db.merge(db_item)
    db.commit()

async def get_cached_data(key: str) -> Dict[str, Any]:
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    db = next(get_db())
    db_item = db.query(CacheItem).filter(CacheItem.key == key).first()
    if db_item:
        data = json.loads(db_item.value)
        redis_client.set(key, db_item.value)
        return data
    return None

def cached(func):
    @wraps(func)
    async def wrapper(*args, force_reload=False, **kwargs):
        if force_reload:
            # Skip cache lookup if force_reload is True
            result = await func(*args, **kwargs)
            key = cache_key(func.__name__, *args, **kwargs)
            await cache_data(key, result)
            return result
        
        key = cache_key(func.__name__, *args, **kwargs)
        cached_result = await get_cached_data(key)
        if cached_result:
            return cached_result
        result = await func(*args, **kwargs)
        await cache_data(key, result)
        return result
    return wrapper