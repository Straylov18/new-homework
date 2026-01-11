from time import sleep
from random import randint

from fastapi.routing import APIRouter

from src.config import settings
from src.service.some_service import get_huge_random_number

router = APIRouter(prefix=settings.BASE_ROUTE_PATH)


@router.get('/some-complex-logic')
async def get_long_response():
    sleep(3)
    return 'Done!'


@router.get('/some-simple-logic')
async def get_fast_response():
    return 'No more calls here!'


@router.get('/endpoint-with-random-complexity')
async def get_random_time_response():
    initial_seed = 0
    for _ in range(randint(5, 1000)):
        initial_seed += get_huge_random_number(100, 200)
    output = 0
    for _ in range(int(initial_seed) % 100):
        output += get_huge_random_number(10_000, 50_000)
    return output
