from functools import lru_cache

from arq.connections import RedisSettings as RedisSettingsArq
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='.env'
    )
    REDIS_SERVER: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_USER: str = 'default'
    REDIS_PASSWORD: str
    REDIS_DB: str = "0"


class ArqSettings(BaseSettings):
    """
    Настройки ARQ (очередь фоновых задач).

    В отличие от Celery, ARQ использует Redis напрямую: он и broker
    (очередь задач), и хранилище результатов задач.
    """
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='.env'
    )

    # Имя очереди, из которой worker забирает задачи.
    ARQ_QUEUE_NAME: str = 'arq:queue'
    # Сколько секунд хранить результат задачи в Redis (keep_result).
    ARQ_JOB_RESULT_TTL: int = 3600
    # Таймаут выполнения одной задачи в секундах (job_timeout).
    ARQ_JOB_TIMEOUT: int = 60
    # Максимум одновременных задач на один воркер.
    ARQ_MAX_JOBS: int = 10


class Settings(BaseSettings):
    """
    Общие настройки приложения.

    Значения по умолчанию рассчитаны на запуск через docker-compose:
      - REDIS_SERVER=redis  (имя сервиса в compose)
      - Когда приложение запускается локально (вне docker), можно
        переопределить эти значения через переменные окружения или .env.
    """
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='.env'
    )

    # FastAPI
    BASE_ROUTE_PATH: str = '/api/v1'

    # Redis и ARQ (вынесены в отдельные классы)
    REDIS: RedisSettings = RedisSettings()
    ARQ: ArqSettings = ArqSettings()

    # Рассылка писем
    EMAIL_LOG_FILE: str = 'data/mail.log'
    # Задержка между "отправкой" писем в секундах (имитация работы)
    EMAIL_SEND_DELAY_SECONDS: float = 2.0

    @property
    def arq_redis_settings(self) -> RedisSettingsArq:
        """
        Настройки подключения к Redis для ARQ.

        ARQ использует Redis напрямую: он и очередь задач (broker), и
        хранилище результатов задач (backend). В отличие от Celery не нужно
        два URL — достаточно одного RedisSettings из arq.connections.
        """
        return RedisSettingsArq(
            host=self.REDIS.REDIS_SERVER,
            port=self.REDIS.REDIS_PORT,
            username=self.REDIS.REDIS_USER,
            password=self.REDIS.REDIS_PASSWORD,
            database=int(self.REDIS.REDIS_DB or 0),
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
