import logging

import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

from src.config import settings
from src.routes.user import router as user_router

log = logging.getLogger("uvicorn")

app = FastAPI(
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs"
)

router = APIRouter(prefix=settings.BASE_ROUTE_PATH)

router.include_router(user_router, prefix='/user', tags=['user'])

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
