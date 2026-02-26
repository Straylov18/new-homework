from fastapi import APIRouter, Depends

from src.adapter.redis import get_redis_connection
from src.service.redis_operations_service import (lpop_list_value,
                                                  push_value_to_list,
                                                  rpop_list_value)

router = APIRouter(prefix='/list')


@router.get('/get-last-list-values')
async def get_last_list_value(redis_session=Depends(get_redis_connection)):
    return await lpop_list_value(redis_session)


@router.get('/get-first-list-values')
async def get_first_list_value(redis_session=Depends(get_redis_connection)):
    return await rpop_list_value(redis_session)


@router.post('/push-list-value/{value}')
async def push_list_value(value: str, redis_session=Depends(get_redis_connection)) -> int:
    return await push_value_to_list(value, redis_session)
