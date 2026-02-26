import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

from src.config import settings
from src.route.redis_hash_table import router as hash_table_router
from src.route.redis_list import router as lists_router
from src.route.redis_string import router as strings_router

app = FastAPI(
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs",
)

router = APIRouter(prefix=settings.BASE_ROUTE_PATH)

router.include_router(strings_router, tags=['string'])
router.include_router(hash_table_router, tags=['hash-table'])
router.include_router(lists_router, tags=['list'])

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
