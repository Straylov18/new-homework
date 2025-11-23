from fastapi import APIRouter

from src.services import get_dominant_color

router = APIRouter()


@router.get('/compare-colors')
async def compare_colors(r: int, g: int, b: int):
    return get_dominant_color(r, g, b)
