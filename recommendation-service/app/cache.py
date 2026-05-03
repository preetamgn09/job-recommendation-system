"""
Redis caching layer for recommendations.
"""
import json
import redis.asyncio as redis
from app.config import settings

redis_client = None


async def connect_redis():
    global redis_client
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    print("✅ Recommendation Service connected to Redis")


async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()


def _cache_key(user_id: str) -> str:
    return f"reco:{user_id}"


async def get_cached_recommendations(user_id: str) -> list | None:
    if not redis_client:
        return None
    try:
        data = await redis_client.get(_cache_key(user_id))
        if data:
            return json.loads(data)
    except Exception:
        pass
    return None


async def cache_recommendations(user_id: str, recommendations: list):
    if not redis_client:
        return
    try:
        await redis_client.setex(
            _cache_key(user_id),
            settings.REDIS_TTL,
            json.dumps(recommendations),
        )
    except Exception:
        pass


async def invalidate_cache(user_id: str):
    if not redis_client:
        return
    try:
        await redis_client.delete(_cache_key(user_id))
    except Exception:
        pass


async def invalidate_all():
    if not redis_client:
        return
    try:
        keys = []
        async for key in redis_client.scan_iter("reco:*"):
            keys.append(key)
        if keys:
            await redis_client.delete(*keys)
    except Exception:
        pass
