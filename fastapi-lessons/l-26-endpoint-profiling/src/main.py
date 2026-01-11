import uvicorn
from fastapi import FastAPI

from src.middleware import ProfilingMiddleware
from src.config import settings
from src.route.some_routes import router

app = FastAPI(
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs",
)

app.add_middleware(ProfilingMiddleware)

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
