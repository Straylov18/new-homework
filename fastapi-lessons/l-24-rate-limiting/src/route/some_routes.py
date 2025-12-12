from time import sleep

from fastapi import Request
from fastapi.routing import APIRouter

from src.config import settings
from src.rate_limiter import limiter

router = APIRouter(prefix=settings.BASE_ROUTE_PATH)


@router.get('/hello')
@limiter.limit("1/second", per_method=True)
@limiter.limit("5/minute", per_method=True)
async def hello_world(request: Request):  # параметр 'request: Request' должен быть
    return 'Hi mam!'


@router.get('/some-complex-logic')
@limiter.limit("5/minute", per_method=True)
async def sleepy_get(request: Request):
    sleep(1)
    return 'Done!'
