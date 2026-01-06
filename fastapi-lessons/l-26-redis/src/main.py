import uvicorn
from fastapi import FastAPI

from src.config import settings
from src.route.some_router import router

app = FastAPI(
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs",
)

app.include_router(router, prefix=settings.BASE_ROUTE_PATH)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
