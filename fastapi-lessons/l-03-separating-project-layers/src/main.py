import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

from src.routes.animal import router as animal_router
from src.routes.human import router as human_router
from src.config import settings

app = FastAPI(
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs",
)

router = APIRouter(prefix=settings.BASE_ROUTE_PATH)

router.include_router(animal_router, prefix='/animal', tags=['animal'])
router.include_router(human_router, prefix='/human', tags=['human'])

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
