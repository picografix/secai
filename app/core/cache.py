import json
import redis
from core.config import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL)

def cache_key(func_name: str, *args, **kwargs) -> str:
    return f"{func_name}:{json.dumps(args)}:{json.dumps(kwargs)}"