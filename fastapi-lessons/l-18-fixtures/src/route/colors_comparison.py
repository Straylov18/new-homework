from fastapi import APIRouter

from src.service.colors_comparison import get_dominant_color
from src.scheme.color import Color

router = APIRouter()


@router.get('/compare-colors')
async def compare_colors(r: int, g: int, b: int):
    return get_dominant_color(r, g, b)


@router.post('/compare-colors-list')
async def compare_colors_list(body: list[Color]) -> list[str]:
    return [get_dominant_color(**dict(c)) for c in body]
