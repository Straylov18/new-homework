from fastapi import APIRouter, Depends

from src.adapter.redis import get_redis_connection
from src.service.some_service import delete_some_string_cache, get_some_string

router = APIRouter()


@router.get('/some-data/{id}')
async def get_same_data(id: str, redis_session=Depends(get_redis_connection)) -> str:
    return await get_some_string(id, redis_session)


@router.delete('/some-data/{id}/clear-cache/')
async def clear_same_data_cache(id: str, redis_session=Depends(get_redis_connection)) -> str:
    await delete_some_string_cache(id, redis_session)
    return f'deleted cache for string with id: {id}'

# TODO about scan keys

# TODO more about set/get hash, list, set etc.

# data = await redis_session.hgetall(id)
# return data if data else None

# await self.redis.hset(id, mapping=data)

# ...
