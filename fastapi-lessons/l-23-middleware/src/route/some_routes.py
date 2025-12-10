from time import sleep

from fastapi.routing import APIRouter

from src.config import settings

router = APIRouter(prefix=settings.BASE_ROUTE_PATH)


@router.get('/hello')
async def hello_world():
    return 'Hi mam!'


@router.get('/some-complex-logic')
async def get_object():
    sleep(3)
    return 'Done!'


@router.get('/only-one-chance')
async def will_be_blocked_in_middleware():
    return 'No more calls here!'
