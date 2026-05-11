import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

from src.config import settings
from src.middleware import MetricsMiddleware
from src.route.app_info import router as app_info_router
from src.route.joke import router as joke_router
from src.route.meme import router as meme_router
from src.route.user import router as user_router

app = FastAPI(
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs",
)

router = APIRouter(prefix=settings.BASE_ROUTE_PATH)

router.include_router(app_info_router, tags=['App info'])
router.include_router(user_router, tags=['User'])
router.include_router(meme_router, tags=['Meme'])
router.include_router(joke_router, tags=['Joke'])

app.include_router(router)

app.add_middleware(MetricsMiddleware)  # type: ignore[arg-type]

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8001,
        reload=True,
    )
