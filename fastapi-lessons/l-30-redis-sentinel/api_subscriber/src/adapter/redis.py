import redis.asyncio as redis

from config import settings


async def get_redis_connection():
    redis_client = await redis.from_url(
        settings.REDIS.REDIS_URI,
        encoding="utf-8",
        decode_responses=True
    )
    try:
        return redis_client
    finally:
        await redis_client.close()
