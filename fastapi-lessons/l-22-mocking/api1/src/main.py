import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

from src.config import settings
from src.route.some_router import router as some_router

app = FastAPI(
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs",
)

router = APIRouter(prefix=settings.BASE_ROUTE_PATH)

router.include_router(some_router, prefix='/some-router', tags=['auth-server-integrations'])

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
