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


async def filter_cache_by_prefix(cache_key_prefix, redis_session):
    return await redis_session.scan(match=f'{cache_key_prefix}*')


HASH_TABLE_NAME = 'some_hash_table'


async def get_all_hash_table_values(redis_session):
    data = await redis_session.hgetall(HASH_TABLE_NAME)
    return data if data else None


async def add_value_to_hash_table(hkey, hvalue, redis_session):
    data = {}
    data[hkey] = hvalue
    await redis_session.hset(HASH_TABLE_NAME, mapping=data)


LIST_NAME = 'some_list'


async def lpop_list_value(redis_session):
    return await redis_session.lpop(LIST_NAME)


async def rpop_list_value(redis_session):
    return await redis_session.rpop(LIST_NAME)


async def push_value_to_list(value, redis_session):
    await redis_session.lpush(LIST_NAME, value)
    return await redis_session.llen(LIST_NAME)
