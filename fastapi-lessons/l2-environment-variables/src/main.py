import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

from src.config import settings

print(f'using base prefix: {settings.BASE_ROUTE_PATH}')

app = FastAPI(
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs",
)

router = APIRouter(prefix=settings.BASE_ROUTE_PATH)


@router.get('/hello-world')
async def hello_world():
    return "Hi mam!"


app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
