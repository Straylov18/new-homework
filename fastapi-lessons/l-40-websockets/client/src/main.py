import json
import queue
import threading

import pygame
import websocket

from config import settings

# Настройки из .env / config.py
WINDOW_WIDTH = settings.WINDOW_WIDTH
WINDOW_HEIGHT = settings.WINDOW_HEIGHT
PLAYER_SIZE = settings.PLAYER_SIZE
MOVE_SPEED = settings.MOVE_SPEED
FPS = settings.FPS
SERVER_URL = settings.SERVER_URL

# Ключи управления: стрелки + WASD
CONTROLS = {
    pygame.K_UP: (0, -1),
    pygame.K_w: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_s: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_a: (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_d: (1, 0),
}


class WebSocketClient:
    """Обёртка над websocket-client, читающая сообщения в отдельном потоке."""

    def __init__(self, url: str) -> None:
        self.url = url
        self.messages: "queue.Queue[dict]" = queue.Queue()
        self.connected = False
        self.ws = None

    def connect(self) -> None:
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        # run_forever блокирует поток — запускаем в фоне.
        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def _on_open(self, ws: object) -> None:
        self.connected = True
        print("[client] подключён к серверу")

    def _on_message(self, ws: object, message: str) -> None:
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            return
        self.messages.put(data)

    def _on_error(self, ws: object, error: Exception) -> None:
        print(f"[client] ошибка WebSocket: {error}")

    def _on_close(self, ws: object, close_status_code: int, close_msg: str) -> None:
        self.connected = False
        print("[client] соединение закрыто")

    def send_move(self, x: int, y: int) -> None:
        if self.ws:
            try:
                self.ws.send(
                    json.dumps({"type": "move", "x": x, "y": y}, ensure_ascii=False)
                )
            except Exception as exc:
                print(f"[client] не удалось отправить ход: {exc}")

    def close(self) -> None:
        if self.ws:
            self.ws.close()


def parse_color(value: str) -> tuple[int, int, int]:
    """Преобразует строку цвета в RGB-кортеж."""
    return pygame.Color(value)


class Game:
    """Состояние локальной игры: игроки + локальный контроллер."""

    def __init__(self) -> None:
        self.my_id: int | None = None
        self.players: dict[int, dict] = {}
        self.local_x = WINDOW_WIDTH // 2
        self.local_y = WINDOW_HEIGHT // 2

    def handle_message(self, data: dict) -> None:
        msg_type = data.get("type")

        if msg_type == "init":
            self.my_id = data["id"]
            for p in data["players"]:
                self.players[p["id"]] = {"x": p["x"], "y": p["y"], "color": p["color"]}

        elif msg_type == "player_join":
            self.players[data["id"]] = {
                "x": data["x"],
                "y": data["y"],
                "color": data["color"],
            }

        elif msg_type == "player_leave":
            self.players.pop(data["id"], None)

        elif msg_type == "move":
            if data["id"] in self.players:
                self.players[data["id"]]["x"] = data["x"]
                self.players[data["id"]]["y"] = data["y"]

    def update_local(self, pressed: dict) -> None:
        """Двигает локального игрока на основе зажатых клавиш."""
        dx, dy = 0, 0
        for key, (kx, ky) in CONTROLS.items():
            if pressed.get(key):
                dx += kx
                dy += ky
        if dx != 0 or dy != 0:
            # Нормализуем диагональ (чтобы не бежать быстрее по диагонали).
            length = (dx * dx + dy * dy) ** 0.5
            self.local_x += int(dx / length * MOVE_SPEED)
            self.local_y += int(dy / length * MOVE_SPEED)
            # Не даём выйти за границы окна.
            self.local_x = max(0, min(WINDOW_WIDTH - PLAYER_SIZE, self.local_x))
            self.local_y = max(0, min(WINDOW_HEIGHT - PLAYER_SIZE, self.local_y))


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("2D Multiplayer (WebSocket)")
    clock = pygame.time.Clock()

    game = Game()
    client = WebSocketClient(SERVER_URL)
    client.connect()

    running = True
    while running:
        # Обрабатываем входящие сообщения сервера.
        while not client.messages.empty():
            game.handle_message(client.messages.get())

        # Обрабатываем события pygame (закрытие окна).
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Текущее состояние клавиатуры (зажатые клавиши).
        keys = pygame.key.get_pressed()
        pressed = {key: bool(keys[key]) for key in CONTROLS.keys()}

        # Обновляем локального игрока и отправляем ход на сервер.
        old_x, old_y = game.local_x, game.local_y
        game.update_local(pressed)
        if (game.local_x, game.local_y) != (old_x, old_y):
            client.send_move(game.local_x, game.local_y)

        # Рисуем фон и всех игроков.
        screen.fill((20, 20, 30))
        font = pygame.font.SysFont(None, 24)
        for pid, player in game.players.items():
            rect = pygame.Rect(player["x"], player["y"], PLAYER_SIZE, PLAYER_SIZE)
            pygame.draw.rect(screen, parse_color(player["color"]), rect)
            # Обводим локального игрока рамкой.
            if pid == game.my_id:
                pygame.draw.rect(screen, (255, 255, 255), rect, 3)
            # Подписываем id игрока.
            label = font.render(str(pid), True, (255, 255, 255))
            screen.blit(label, (player["x"], player["y"] - 20))

        status = f"Your id: {game.my_id} | Connected: {client.connected}"
        screen.blit(font.render(status, True, (200, 200, 200)), (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    client.close()
    pygame.quit()


if __name__ == "__main__":
    main()
