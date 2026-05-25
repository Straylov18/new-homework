# import fastapi_swagger_dark as fsd
import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

from src.config import APP_VERSION, settings
from src.route.app_info import router as app_info_router
from src.route.helicopter import router as helicopter_router

app = FastAPI(
    title="Connections-reminder",
    version=APP_VERSION,
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs",
)

router = APIRouter(prefix=settings.BASE_ROUTE_PATH)
# fsd.install(router, path="/swagger-docs")

router.include_router(app_info_router, tags=['App info'])
router.include_router(helicopter_router, tags=['Helicopter'])

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
