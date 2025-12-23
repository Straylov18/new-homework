import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

from src.config import settings
from src.route.auth import router as auth_router
from src.route.user import router as user_router
from src.route.user_post import router as user_post_router

app = FastAPI(
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs",
)

router = APIRouter(prefix=settings.BASE_ROUTE_PATH)

router.include_router(auth_router, prefix='/auth', tags=['auth'])
router.include_router(user_router, prefix='/user', tags=['user'])
router.include_router(user_post_router, prefix='/user-post', tags=['user_post'])

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
