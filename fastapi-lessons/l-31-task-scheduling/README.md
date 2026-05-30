# Планировщик задач

Порой при разработке бэкенда встает необходимость делать какие-то однотипные задачи с определенной периодичностью.
Конечно к данному моменту курса скорее всего 
ты уже умеешь задавать периодические задачи при помощи cron таблиц в линуксе 
(допустим можно написать cron задачи, дергающие ручки бэкенда). 
Однако было бы удобнее описывать такие задачи внутри бэкенд приложения, 
да и порой возникает необходимость например приостанавливать такие периодические задачи, 
редактировать их или добавлять новые при определенных событиях на бэкенде.

Для этого существуют множество библиотек для планирования задач.

## Использование простого планировщика задач на примере apscheduler

В данном уроке мы будем встраивать планировщик задач на основе библиотеки apscheduler.
С помощью этой библиотеки (на данный момент) 
проще всего сделать планировщик задач для небольших приложений.

Также планировщик достаточно часто делают с помощью celery, 
что даже удобнее в случае больших приложений, но немного сложнее.
Еще как исключительно асинхронный планировщик задач порой использую ARQ 
(если все фоновые задачи будут асинхронные, 
и в качестве брокера сообщений бриложение уже используется Redis).
Их мы подробнее рассмотрим в следующих уроках.

### Идея данного приложения

В данном уроке мы реализуем проект, 
в котором периодические задачи будут добавлять в БД новые таски.
По умолчанию при старте приложения таски будут добавляться раз в определенный период.

У приложения также будут ручки для добавления новых периодических фоновых задач по 
добавлению тасок в БД, просмотра списка этих фоновых задач, их изменения и удаления.

Поскольку для планировщика мы введем в приложении новый слой кода, 
нам будет удобнее производить операции с БД из слоя репозитория.

Пусть таска, которая у нас будет храниться в postgres БД, 
будет описываться в **src/model/task.py** моделью:
```python
import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, UUID, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.adapter.db.session import Base


class Task(Base):
    __tablename__ = 'task'

    uid: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    description: Mapped[str] = mapped_column(String, nullable=False)
    date_created: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    scheduler_id: Mapped[str] = mapped_column(String, nullable=False)
```

Пользователь извне сможет только лишь получать все таски при помощи ручки 
(описана в **src/route/task.py**):
```python
from fastapi import APIRouter

from src.scheme.task import TaskInfo
from src.service.task import TaskService

router = APIRouter()


@router.get('/list')
async def get_tasks_list() -> list[TaskInfo]:
    return await TaskService.get_tasks_list()
```

Схемы же для тасок в **src/scheme/task.py** будут следующие:
```python
from datetime import datetime

from pydantic import UUID4, BaseModel, Field


class TaskCreate(BaseModel):
    description: str | None = Field(description="Task description", default=None)
    scheduler_id: str = Field(description="Scheduler id")


class TaskInfo(BaseModel):
    uid: UUID4 = Field(description="Task uid")
    description: str | None = Field(description="Task description", default=None)
    date_created: datetime = Field(description="The date when task was created")
    scheduler_id: str = Field(description="Scheduler id")
```

Сервис же для таски будет описан в **src/service/task.py** и выглядеть будет следующим образом:
```python
from src.container.repository import repository_container
from src.scheme.task import TaskCreate, TaskInfo


class TaskService:

    @staticmethod
    async def create_task(data: TaskCreate) -> TaskInfo:
        new_task = await repository_container.task_repository().add_one(data.model_dump(exclude_unset=True))
        return new_task

    @staticmethod
    async def get_tasks_list() -> list[TaskInfo]:
        tasks = await repository_container.task_repository().get_list()
        return tasks
```

Все обвязки для репозитория тасок и контейнера репозиториев же мы опишем по аналогии с 14-м уроком.

Поскольку в данном уроке нам будет необходимо наблюдать большое количество выводов в логи, 
логирование мы тоже сделаем по-нормальному по аналогии с 11-м уроком.

### Подключение планировщика

Установим apscheduler:
```shell
poetry add apscheduler
```

Поскольку планировщик периодических задач необходим в единственном экземпляре на все приложение, 
можно запихнуть его в контейнер и генерировать при первом обращении к контейнеру.
Опишем это в **src/container/scheduler.py**:
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class SchedulerContainer:
    scheduler: AsyncIOScheduler = None

    @classmethod
    def get_scheduler(cls) -> AsyncIOScheduler:
        if cls.scheduler is None:
            cls.scheduler = AsyncIOScheduler()

        return cls.scheduler
```

Опишем слой сервиса под создание периодических задач для нашего планировщика в **src/service/scheduler_job.py**:
```python
import logging

from apscheduler.triggers.interval import IntervalTrigger

from src.container.scheduler import SchedulerContainer
from src.scheduler.task_scheduler import schedule_task
from src.scheme.scheduler_job import SchedulerJob

logger = logging.getLogger(__name__)


class SchedulerJobService:

    @staticmethod
    async def create_task_scheduler_job(data: SchedulerJob):
        current_scheduler_id = data.id
        scheduler = SchedulerContainer.get_scheduler()
        scheduler.add_job(
            schedule_task,
            trigger=IntervalTrigger(seconds=data.period),
            id=current_scheduler_id,
            replace_existing=True,
            kwargs={'scheduler_id': current_scheduler_id}
        )
        logger.info(f'created new job: {scheduler.get_job(current_scheduler_id)}')

    @staticmethod
    async def get_task_scheduler_jobs_list() -> list[SchedulerJob]:
        output = []
        for j in SchedulerContainer.get_scheduler().get_jobs():
            output.append(SchedulerJob(
                id=j.id,
                period=j.trigger.interval.seconds
            ))
        return output

    @staticmethod
    async def remove_task_scheduler_job(scheduler_job_id):
        SchedulerContainer.get_scheduler().remove_job(scheduler_job_id)
```
Здесь 
- в методе ```create_task_scheduler_job``` при помощи вызова ```add_job``` добавляется новая запланированная задача, 
которая будет вызывать функцию ```schedule_task``` с параметрами заданными в ```kwargs``` 
(```kwargs={'scheduler_id': current_scheduler_id}```), 
будет периодической (```trigger=IntervalTrigger(seconds=data.period)```), 
будет иметь конкретный id (```id=current_scheduler_id```),
будет заменять задачу с таким же id, если такая есть (```replace_existing=True```)
- в методе ```get_task_scheduler_jobs_list``` получается весь список задач (```.get_jobs()```)
- в методе ```remove_task_scheduler_job``` задача удаляется по id (```.remove_job(scheduler_job_id)```)

Сами же функции, которые будут вызываться периодическими задачами, 
мы опишем в отдельном слое в **src/scheduler/task_scheduler.py**:
```python
import logging

from src.container.scheduler import SchedulerContainer
from src.scheme.task import TaskCreate
from src.service.task import TaskService

logger = logging.getLogger(__name__)

scheduler = SchedulerContainer.get_scheduler()


async def schedule_task(scheduler_id: str):
    task_info = TaskCreate(
        description=f'task created by scheduler with id {scheduler_id}',
        scheduler_id=scheduler_id
    )
    await TaskService.create_task(task_info)
    logger.info(f'Task created by scheduler {scheduler_id}')
```

Теперь нужно инициализировать наш планировщик задач.
Можем сделать это допустим в lifespan перед созданием fastapi приложения
(через метод описания жизненного цикла fastapi приложения).

Выглядеть это должно примерно так:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        SchedulerContainer.get_scheduler().start()
        logger.info('Task scheduler started')
        yield
    except Exception as e:
        logger.error(f'Task scheduler default job initialization errors: {e}')
    finally:
        SchedulerContainer.get_scheduler().shutdown()
        logger.info('Task scheduler job stopped')


app = FastAPI(lifespan=lifespan)
```

Можно также сразу добавлять периодическую задачку при инициализации, 
чтобы при старте приложения оно сразу начинало генерить таски:
```python
default_scheduler_id = 'default_create_task_job'
SchedulerContainer.get_scheduler().add_job(
    schedule_task,
    trigger=IntervalTrigger(seconds=settings.DEFAULT_SCHEDULING_PERIOD),
    id=default_scheduler_id,
    replace_existing=True,
    kwargs={'scheduler_id': default_scheduler_id}
)
```

При остановке приложения же если необходимо мы можем вместо:
```python
SchedulerContainer.get_scheduler().shutdown()
```
вызывать:
```python
SchedulerContainer.get_scheduler().shutdown(wait=True)
```
чтобы приложение завершении ждало, 
пока все джобы нашего планировщика не завершат свою работу.

Тогда **src/main.py** будет выглядеть следующим образом:
```python
import logging
from contextlib import asynccontextmanager

import uvicorn
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI
from fastapi.routing import APIRouter

from src.config import settings
from src.container.scheduler import SchedulerContainer
from src.route.scheduler_job import router as task_scheduler_router
from src.route.task import router as task_router
from src.scheduler.task_scheduler import schedule_task

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        default_scheduler_id = 'default_create_task_job'
        SchedulerContainer.get_scheduler().add_job(
            schedule_task,
            trigger=IntervalTrigger(seconds=settings.DEFAULT_SCHEDULING_PERIOD),
            id=default_scheduler_id,
            replace_existing=True,
            kwargs={'scheduler_id': default_scheduler_id}
        )
        SchedulerContainer.get_scheduler().start()
        logger.info('Task scheduler started')
        yield
    except Exception as e:
        logger.error(f'Task scheduler default job initialization errors: {e}')
    finally:
        SchedulerContainer.get_scheduler().shutdown()
        # SchedulerContainer.get_scheduler().shutdown(wait=True)
        logger.info('Task scheduler job stopped')


app = FastAPI(
    openapi_url=f'{settings.BASE_ROUTE_PATH}/openapi.json',
    docs_url=f'{settings.BASE_ROUTE_PATH}/docs',
    lifespan=lifespan,
)

router = APIRouter(prefix=settings.BASE_ROUTE_PATH)

router.include_router(task_router, prefix='/task', tags=['task'])
router.include_router(task_scheduler_router, prefix='/task_scheduler', tags=['task_scheduler'])

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
```

Чтобы можно было создать дополнительные периодические задачи извне, 
и удобнее пронаблюдать механизм работы планировщика, 
добавим ручки на создание периодических задач в **src/route/scheduler_job.py**:
```python
import logging

from fastapi import APIRouter

from src.scheme.scheduler_job import SchedulerJob
from src.service.scheduler_job import SchedulerJobService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get('/list')
async def get_task_scheduler_jobs_list() -> list[SchedulerJob]:
    return await SchedulerJobService.get_task_scheduler_jobs_list()


@router.post('/')
async def create_task_scheduler_job(data: SchedulerJob):
    task_scheduler = await SchedulerJobService.create_task_scheduler_job(data)
    logger.info(f'Created new scheduler {task_scheduler}')
    return 'scheduler changed'


@router.delete('/{scheduler_id}')
async def remove_task_scheduler_job(scheduler_id: str):
    await SchedulerJobService.remove_task_scheduler_job(scheduler_id)
    logger.info(f'Scheduler with id {scheduler_id} was removed')
    return 'scheduler removed'
```
Здесь у нас будут доступны ручки на просмотр списка всех периодических задач, 
добавление и удаление периодических задач.

### Использование декораторов для описания периодических задач

Если же планируемые задачи необходимо создать только при старте приложения, 
удобнее всего просто прикрутить ее к исполняемой функции при помощи декоратора.
Добавим такую функцию с декоратором в нашем слое планировщика в **src/scheduler/task_scheduler.py**:
```python
@scheduler.scheduled_job('interval', id='warning_job_from_decorator_id', seconds=2)
async def job_from_decorator():
    logger.warning('called from func scheduled with decorator')
```

### Проблема хранения информации о запланированных задачах

На данный момент информация о запланированных задачах храниться в конкретном бэкенде, 
на котором они будут выполняться.
Достаточно часто встречаются случаи, 
когда необходимо развернуть несколько сущностей бэкенда, 
чтобы распределить между ними нагрузку.

Проверим, что сейчас с этим у нас есть проблемы, запустив приложение на нескольких uvicorn воркерах:
```shell
poetry run uvicorn src.main:app --workers 4
# make run_uvcorn_4_workers
```

Если сейчас мы будем дергать ручки изменения периодических задач, 
их будет обрабатывать один из воркеров, 
который будет менять эту информацию только у себя, не передавая остальным.

### Хранение задач в redis

И если мы хотим допустим,
чтобы какая-то задача периодически выполнялась сразу несколькими бэкендами,
то нам необходимо как-то передавать информацию об изменении
или создании запланированной задачи между ними.

Для подобных целей зачастую используют redis.
У данной библиотеки уже есть встроенная возможность интеграции с redis, 
чтобы хранить в нем информации о запланированных задачах.

```python
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.config import settings


class SchedulerContainer:
    scheduler: AsyncIOScheduler = None

    @classmethod
    def get_scheduler(cls) -> AsyncIOScheduler:
        if cls.scheduler is None:
            jobstores = {
                'default': RedisJobStore(
                    jobs_key='dispatched_tasks_jobs',
                    run_times_key='dispatched_tasks_running',
                    host=settings.REDIS.REDIS_SERVER,
                    port=settings.REDIS.REDIS_PORT,
                    db=settings.REDIS.REDIS_DB,
                    username=settings.REDIS.REDIS_USER,
                    password=settings.REDIS.REDIS_PASSWORD,
                )
            }
            cls.scheduler = AsyncIOScheduler(jobstores=jobstores)

        return cls.scheduler
```
Здесь мы указали в какую БД редиса будет писаться информация о наших запланированных задачах.

Теперь эта информация будет при старте автоматически подтягиваться всеми бэкендами, 
которые подключены к этому редису.

Добавим настройки подключения к redis в **src/config.py**:
```python
import logging.config
from typing import Any

from pydantic import PostgresDsn, RedisDsn, field_validator
from pydantic_core.core_schema import ValidationInfo
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

    REDIS_URI: str | None = None

    @field_validator('REDIS_URI', mode='before')
    @classmethod
    def assemble_redis_connection(cls, v: str | None, info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        return str(RedisDsn.build(
            scheme='redis',
            username=info.data.get('REDIS_USER'),
            password=info.data.get('REDIS_PASSWORD'),
            host=info.data.get('REDIS_SERVER'),
            port=info.data.get('REDIS_PORT'),
            path=info.data.get('REDIS_DB') or '0',
        ))


class PostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='.env'
    )
    POSTGRES_SERVER: str = 'localhost'
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "postgres"
    POSTGRES_DB_ECHO: bool = True

    SQLALCHEMY_DATABASE_URI: str | None = None
    SQLALCHEMY_DATABASE_URI_ASYNC: str | None = None

    PROFILE_QUERY_MODE: bool = False

    @field_validator('SQLALCHEMY_DATABASE_URI', mode='before')
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        return str(PostgresDsn.build(
            scheme='postgresql+psycopg',
            username=info.data.get('POSTGRES_USER'),
            password=info.data.get('POSTGRES_PASSWORD'),
            host=info.data.get('POSTGRES_SERVER'),
            port=info.data.get('POSTGRES_PORT'),
            path=info.data.get('POSTGRES_DB') or '',
        ))

    @field_validator('SQLALCHEMY_DATABASE_URI_ASYNC', mode='before')
    @classmethod
    def assemble_async_db_connection(cls, v: str | None, info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        return info.data.get('SQLALCHEMY_DATABASE_URI')


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='.env'
    )
    BASE_ROUTE_PATH: str = '/api/v1'
    DEFAULT_SCHEDULING_PERIOD: int = 3
    POSTGRES: PostgresSettings = PostgresSettings()
    REDIS: RedisSettings = RedisSettings()
    LOG_LEVEL: str = 'INFO'


settings = Settings()

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {"default": {"format": "%(asctime)s [%(process)s] %(levelname)s: %(message)s"}},
    "handlers": {
        "console": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "level": settings.LOG_LEVEL,
        }
    },
    "root": {"handlers": ["console"], "level": settings.LOG_LEVEL},
    "loggers": {
        "gunicorn": {"propagate": True},
        "gunicorn.access": {"propagate": True},
        "gunicorn.error": {"propagate": True},
        "uvicorn": {"propagate": True},
        "uvicorn.access": {"propagate": True},
        "uvicorn.error": {"propagate": True},
    },
}

logging.config.dictConfig(LOG_CONFIG)
```

Тогда **src/.env** будет выглядеть следующим образом:
```
BASE_ROUTE_PATH='/api/v1'
LOG_LEVEL='INFO'

DEFAULT_SCHEDULING_PERIOD=50

# Postgres
POSTGRES_SERVER=localhost
POSTGRES_PORT=5435
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=master

# Redis
REDIS_SERVER=localhost
REDIS_PORT=6380
REDIS_DB=0
REDIS_USER=default
REDIS_PASSWORD=master
```

Теперь если например запустить наш бэкенд на нескольких воркера:
```shell
poetry run uvicorn src.main:app --workers 4
# make run_uvcorn_4_workers
```
То при изменении запланированной задачи в одном воркере бэкенда, 
она будет изменяться у всех.
Это можно проверить сделав запрос в наш бэкенд.
Его обработает лишь один из воркеров бэкенда, 
а периодическая задача измениться у всех.

Таким образом можно будет синхронизовать запланированные задачи даже для нескольких узлов бэкенда, 
развернутых на разных серверах.

Более подробно о функционале библиотеки apscheduler можно почитать тут: 
https://apscheduler.readthedocs.io/en/stable/userguide.html.
