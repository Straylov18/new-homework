from fastapi import APIRouter, Depends

from src.adapter.redis import get_redis_connection
from src.service.redis_operations_service import (add_value_to_hash_table,
                                                  get_all_hash_table_values)

router = APIRouter()


@router.get('/get-all-hash-table-values')
async def get_hash_table_values(redis_session=Depends(get_redis_connection)):
    return await get_all_hash_table_values(redis_session)


@router.post('/set-hash-table-value/{hkey}/{hvalue}')
async def set_hash_table_value(hkey: str, hvalue: str, redis_session=Depends(get_redis_connection)):
    return await add_value_to_hash_table(hkey, hvalue, redis_session)
