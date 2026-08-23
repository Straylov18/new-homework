"""WebSocket-хендлер: основной игровой канал."""

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.container.room import RoomContainer

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Клиент подключается, двигает игрока, получает координаты всех игроков."""
    room = RoomContainer.get_room()
    await websocket.accept()

    # Регистрируем нового игрока со случайным цветом и стартовой позицией.
    player_id, color, start_x, start_y = room.spawn_player()
    room.connect(player_id, websocket)

    # Отправляем клиенту его id и полный снимок текущих игроков.
    await room.send(player_id, {"type": "init", "id": player_id, "players": room._snapshot()})

    # Сообщаем всем (включая нового) о появлении игрока.
    await room.broadcast(
        {
            "type": "player_join",
            "id": player_id,
            "x": start_x,
            "y": start_y,
            "color": color,
        }
    )

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if data.get("type") == "move":
                x = float(data.get("x", start_x))
                y = float(data.get("y", start_y))
                room.move_player(player_id, x, y)
                # Рассылаем новое положение всем игрокам.
                await room.broadcast({"type": "move", "id": player_id, "x": x, "y": y})
    except WebSocketDisconnect:
        pass
    finally:
        # При отключении убираем игрока и оповещаем остальных.
        room.remove_player(player_id)
        await room.broadcast({"type": "player_leave", "id": player_id})
