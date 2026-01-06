import aioredis

from src.config import settings


async def get_redis_connection():
    redis = await aioredis.from_url(
        settings.REDIS.REDIS_URI,
        encoding="utf-8",
        decode_responses=True
    )
    try:
        yield redis
    finally:
        await redis.close()
