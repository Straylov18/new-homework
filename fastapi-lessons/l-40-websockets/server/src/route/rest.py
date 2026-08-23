"""REST-хендлеры: простые эндпоинты для проверки и просмотра игроков."""

from typing import Any

from fastapi import APIRouter, Depends

from src.game.room import GameRoom

router = APIRouter()


def get_room() -> GameRoom:
    # В реальном проекте комнату обычно подтягивают из DI-контейнера.
    from src.main import room

    return room


@router.get("/")
async def root() -> dict[str, str]:
    return {"message": "2D Game WebSocket Server is running"}


@router.get("/players")
async def list_players(room: GameRoom = Depends(get_room)) -> list[dict[str, Any]]:
    """Простой GET-эндпоинт, чтобы посмотреть игроков из браузера."""
    return room._snapshot()
