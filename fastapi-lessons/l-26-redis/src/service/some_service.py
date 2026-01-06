from time import sleep

from src.config import settings


async def long_string_generation(id: str) -> str:
    print('generating new value')
    sleep(2)
    return f'string with id: {id}'


async def get_some_string(id, redis_session):
    cashed_value = await redis_session.get(id)
    if cashed_value is not None:
        return cashed_value

    new_value = await long_string_generation(id)
    await redis_session.set(id, new_value, settings.REDIS.REDIS_CACHE_EXPIRE_TIME)
    # to set expire time separetly
    # await redis_session.expire(id, 3)
    return new_value


async def delete_some_string_cache(id, redis_session):
    await redis_session.delete(id)
