from fastapi import APIRouter

from src.service.math_funcs import divide_and_conquer, get_dominant_color, my_factorial

router = APIRouter()


@router.get('/compare-colors')
async def compare_colors(r: int, g: int, b: int):
    return get_dominant_color(r, g, b)


@router.get('/divide_and_conquer')
async def get_for_divide_and_conquer(num: int, denum: int):
    return divide_and_conquer(num, denum)


@router.get('/factorial')
async def get_for_divide_and_conquer(n: int):
    return my_factorial(n)
