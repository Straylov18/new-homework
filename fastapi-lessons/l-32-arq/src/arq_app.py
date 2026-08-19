"""
ARQ worker settings.

ARQ — это лёгкая очередь фоновых задач поверх Redis. В отличие от Celery
не нужно отдельно настраивать broker и backend: Redis используется напрямую,
а задача — это просто `async def`-функция.

Чтобы запустить worker, выполните:

    arq src.arq_app.WorkerSettings

`WorkerSettings` — конвенция ARQ: CLI импортирует модуль и ищет в нём класс
с этим именем, затем из его атрибутов собирает параметры для Worker
(см. `get_kwargs` в arq.worker). Подклассом чего-либо он быть не обязан —
достаточно класса с нужными атрибутами.

FastAPI (продюсер) и worker (потребитель) используют один и тот же Redis
и одно и то же имя очереди, поэтому согласуйте их с src.config.
"""
from arq.connections import RedisSettings

from src.config import settings
from src.tasks.email_tasks import send_email, send_many_emails

# Настройки подключения к Redis для ARQ, собранные из .env (см. src.config).
redis_settings: RedisSettings = settings.arq_redis_settings


class WorkerSettings:
    """
    Конфигурация ARQ-воркера.

    CLI запускает `arq src.arq_app.WorkerSettings` и через `get_kwargs`
    выбирает из этого класса только те атрибуты, которые совпадают
    с параметрами `arq.worker.Worker.__init__`.

    Атрибуты класса здесь берутся из настроек приложения (src.config):
    так API и worker гарантированно работают с одной очередью и Redis.
    """

    # Функции, которые умеет выполнять этот worker.
    functions = [send_many_emails, send_email]

    # Подключение к Redis (очередь + хранение результатов задач).
    redis_settings = redis_settings

    # Имя очереди задач.
    queue_name = settings.ARQ.ARQ_QUEUE_NAME

    # Сколько секунд хранить результат задачи в Redis (keep_result).
    keep_result = settings.ARQ.ARQ_JOB_RESULT_TTL

    # Максимум одновременных задач на один воркер.
    max_jobs = settings.ARQ.ARQ_MAX_JOBS

    # Таймаут выполнения одной задачи в секундах. Если задача не уложилась,
    # она считается проваленной.
    job_timeout = settings.ARQ.ARQ_JOB_TIMEOUT
