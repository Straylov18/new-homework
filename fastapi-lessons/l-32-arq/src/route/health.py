"""
Health-check эндпоинт.

Вынесен из src.main в отдельный роут, чтобы точка входа приложения
оставалась максимально чистой.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=['Health'])
def health() -> dict[str, str]:
    """Простой health-check."""
    return {"status": "ok"}
