import uvicorn
from fastapi import FastAPI

from src.config import settings
from src.route.redis_hash_table import router as hash_table_router
from src.route.redis_list import router as lists_router
from src.route.redis_string import router as strings_router

app = FastAPI(
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs",
)

app.include_router(strings_router, prefix=f'{settings.BASE_ROUTE_PATH}/string', tags=['string'])
app.include_router(hash_table_router, prefix=f'{settings.BASE_ROUTE_PATH}/hash-table', tags=['hash-table'])
app.include_router(lists_router, prefix=f'{settings.BASE_ROUTE_PATH}/list', tags=['list'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
