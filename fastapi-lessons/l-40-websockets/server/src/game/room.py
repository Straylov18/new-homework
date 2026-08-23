import json
from typing import Any

from fastapi import WebSocket


class GameRoom:
    """Слой игры: хранит игроков, их координаты и активные соединения.

    Не зависит от HTTP/WebSocket-фреймворка напрямую (использует только
    абстракцию WebSocket), поэтому логику можно переиспользовать.
    """

    # Палитра цветов для новых игроков.
    COLORS = ["red", "green", "blue", "yellow", "purple", "orange"]

    def __init__(self) -> None:
        # player_id -> dict с координатами (x, y) и цветом
        self.players: dict[int, dict[str, Any]] = {}
        # player_id -> активное WebSocket-соединение
        self.connections: dict[int, WebSocket] = {}
        self._next_id = 1

    def _next_player_id(self) -> int:
        player_id = self._next_id
        self._next_id += 1
        return player_id

    def _snapshot(self) -> list[dict[str, Any]]:
        """Текущее состояние всех игроков для отдачи новому клиенту."""
        return [
            {"id": pid, "x": p["x"], "y": p["y"], "color": p["color"]}
            for pid, p in self.players.items()
        ]

    def spawn_player(self) -> tuple[int, str, float, float]:
        """Регистрирует нового игрока и возвращает (id, color, x, y)."""
        player_id = self._next_player_id()
        color = self.COLORS[player_id % len(self.COLORS)]
        x = 50.0 + (player_id * 20) % 500
        y = 50.0 + (player_id * 30) % 300
        self.players[player_id] = {"color": color, "x": x, "y": y}
        return player_id, color, x, y

    def connect(self, player_id: int, ws: WebSocket) -> None:
        """Привязывает WebSocket-соединение к игроку."""
        self.connections[player_id] = ws

    def add_player(
        self, player_id: int, color: str, x: float, y: float
    ) -> None:
        self.players[player_id] = {"color": color, "x": x, "y": y}

    def move_player(self, player_id: int, x: float, y: float) -> None:
        if player_id in self.players:
            self.players[player_id]["x"] = x
            self.players[player_id]["y"] = y

    def remove_player(self, player_id: int) -> None:
        self.players.pop(player_id, None)
        self.connections.pop(player_id, None)

    async def send(self, player_id: int, message: dict[str, Any]) -> None:
        """Отправить сообщение одному игроку по его соединению."""
        ws = self.connections.get(player_id)
        if ws is not None:
            await ws.send_text(json.dumps(message, ensure_ascii=False))

    async def broadcast(self, message: dict[str, Any]) -> None:
        """Отправить сообщение всем подключённым клиентам."""
        payload = json.dumps(message, ensure_ascii=False)
        dead: list[int] = []
        for player_id, ws in self.connections.items():
            try:
                await ws.send_text(payload)
            except Exception:
                # Если соединение оборвалось, пометим его на удаление.
                dead.append(player_id)
        for player_id in dead:
            self.remove_player(player_id)
