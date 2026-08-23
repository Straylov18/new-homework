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
