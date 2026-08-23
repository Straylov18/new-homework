"""REST-хендлеры: простые эндпоинты для проверки и просмотра игроков."""

from typing import Any

from fastapi import APIRouter, Depends

from src.container.room import RoomContainer
from src.game.room import GameRoom

router = APIRouter()


@router.get("/")
async def root() -> dict[str, str]:
    return {"message": "2D Game WebSocket Server is running"}


@router.get("/players")
async def list_players(room: GameRoom = Depends(RoomContainer.get_room)) -> list[dict[str, Any]]:
    """Простой GET-эндпоинт, чтобы посмотреть игроков из браузера."""
    return room._snapshot()
