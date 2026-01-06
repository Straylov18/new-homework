from fastapi import APIRouter, Depends

from src.adapter.redis import get_redis_connection
from src.service.redis_operations_service import (delete_some_string_cache,
                                                  filter_cache_by_prefix,
                                                  get_some_string)

router = APIRouter()


@router.get('/some-data/{id}')
async def get_same_data(id: str, redis_session=Depends(get_redis_connection)) -> str:
    return await get_some_string(id, redis_session)


@router.delete('/some-data/{id}/clear-cache/')
async def clear_same_data_cache(id: str, redis_session=Depends(get_redis_connection)) -> str:
    await delete_some_string_cache(id, redis_session)
    return f'deleted cache for string with id: {id}'


@router.get('/get-all-cache-with-prefix/{cache_key_prefix}')
async def get_all_cache_with_prefix(cache_key_prefix: str, redis_session=Depends(get_redis_connection)):
    return await filter_cache_by_prefix(cache_key_prefix, redis_session)
