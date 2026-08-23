# WebSocket соединение с сервером на примере 2D мультиплеер игры (FastAPI + pygame)

Как ты помнишь из предыдущих уроков REST работает по модели «запрос-ответ» (pull): 
клиент сам инициирует общение, отправляет запрос, получает ответ, сразу после этого связь завершается.

Однако существует ряд задачь, где серверу необходимо также иметь возможность инициировать отправку данных на клиент 
или же где-то нужно с клиента очень часто постоянно передовать все новые и новые данные.
В таких ситуациях открывать и закрывать соединения все время было бы накладно.

Для таких ситуаций есть множество специальных протоколов, часть из них даже основано на http (например gRPC), 
правда только начиная со второй версии, 
поэтому определенная часть браузеров на данный момент все еще может их не поддерживать.
Поэтому еще долгое время будет популярен протокол WebSocket, 
он после установки соединения создаёт постоянный двусторонний канал: 
сервер может сам «проталкивать» (push) данные клиенту, как только они появляются, без новых запросов.

В этом уроке мы реализуем простую real-time 2D игру, 
в которой куча игроков смогут подключаться данными 
и обмениваться информацией о своем положении при помощим **WebSocket**.

Игроки управляют квадратами, которые двигаются по экрану, а их координаты синхронизируются
между всеми подключёнными клиентами через сервер.

```
┌────────────┐   WS /ws   ┌────────────────────────┐   WS /ws   ┌────────────┐
│ pygame 1   │ ◄────────► │  FastAPI GameRoom      │ ◄────────► │ pygame 2   │
│ (клиент)   │            │  (хранит координаты)   │            │ (клиент)   │
└────────────┘            └────────────────────────┘            └────────────┘
```

## Структура клиента и сервера

### Структура сервера

Для начала опишем логику игровой комнаты.
Ее мы вынесем в отдельный слой **server/src/game/room.py**:
```python
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
```
Здесь в классе `GameRoom` мы будем при подключении (обрабатывается в методе `connect`) 
будем хранить подключения игроков в виде стандартных объектов библиотеки FastAPI - `WebSocket`, 
поскольку все оповещения клиентов мы будем делать в дальнейшем через эти объекты 
(методы `send` для конкретного клиента и `broadcast` для рассылки всем сразу).

Напишем контейнер для игровой комнаты в **server/src/container/room.py**:
```python
from abc import ABC
from src.game.room import GameRoom


class RoomContainer(ABC):
    _game_room: GameRoom | None = None

    @classmethod
    def get_room(cls) -> GameRoom:
        if cls._game_room is None:
            cls._game_room = GameRoom()
        return cls._game_room
```

Напишем обработчик ручки вебсокета, основанный на `GameRoom` классе в **server/src/route/ws.py**:
```python
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.game.room import GameRoom
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
```
Здесь соединение будет идти до тех пор, пока будет происходить обработка `websocket_endpoint` метода, 
поэтому сразу после обмена данными о бользователе наш сервер уходит в бесконечный цикл. 
В рамках этого цикла сервер ждет от клиентов новую информацию, 
и в случае получения такой уведомляет все остальные клиенты об изменениях. 

Также допишем дополнительные REST ручки для обработки healthcheck вызовов в контейнер (`root` метод)
и для получения какой-то информации для условного админа сервера (конкретно здесь листа игоков: `list_players` метод).
Опишем это все в **server/src/route/rest.py**:
```python
from typing import Any

from fastapi import APIRouter, Depends

from src.game.room import GameRoom
from src.container.room import RoomContainer

router = APIRouter()


@router.get("/")
async def root() -> dict[str, str]:
    return {"message": "2D Game WebSocket Server is running"}


@router.get("/players")
async def list_players(room: GameRoom = Depends(RoomContainer.get_room())) -> list[dict[str, Any]]:
    """Простой GET-эндпоинт, чтобы посмотреть игроков из браузера."""
    return room._snapshot()
```

И закинем все это в **server/src/main.py**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.route import rest, ws

app = FastAPI(title="2D Game WebSocket Server")

# Разрешаем подключения к клиенту с любого источника (для простого pygame-клиента).
# В реальном проекте стоит ограничить список origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрируем REST и WebSocket хендлеры из слоя route/.
app.include_router(rest.router)
app.include_router(ws.router)
```

### Структура клиента

В клиенте же мы при старет программы:
- создаем соединение с сервером
- создаем игровой цикл `pygame`приложения
- в этом цикле все время обрабатываем входящие от сервера сообщения
- отправляем текущее положение игрока, если оно изменилось

Подробнее про текущую структуру клиента и всервера можешь почитать в **README.md** в соответствующих директориях модулей.
