from slowapi import Limiter
from slowapi.util import get_remote_address

from src.config import settings

limiter = Limiter(
    key_func=get_remote_address,  # функция проверяет уникальность клиента по адресу (можно пропихивать сюда свою)
    strategy="fixed-window",  # фиксированные периоды (а можно например сделать так, чтобы время между запросами каждый раз увеличивалось)
    storage_uri="memory://",  # храним информацию о последних запросах в памяти
    enabled=settings.RATE_LIMITING_ENABLED,
)
