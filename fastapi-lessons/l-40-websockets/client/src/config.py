from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки клиента, подтягиваются из .env (или переменных окружения)."""

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Адрес WebSocket-сервера (например ws://127.0.0.1:8000/ws)
    SERVER_URL: str = "ws://127.0.0.1:8000/ws"

    # Размеры окна pygame
    WINDOW_WIDTH: int = 800
    WINDOW_HEIGHT: int = 600

    # Параметры игры
    PLAYER_SIZE: int = 30
    MOVE_SPEED: int = 5
    FPS: int = 60


# Единый экземпляр настроек для всего приложения.
settings = Settings()
