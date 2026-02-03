# Планировщик задач

[//]: # (TODO зачем и когда)

## Использование простого планировщика задач на примере apscheduler

В данном уроке мы будем встраивать планировщик задач на основе библиотеки apscheduler.
С помощью этой библиотеки (на данный момент) 
проще всего сделать планировщик задач для небольших приложений.

Также планировщик достаточно часто делают с помощью celery, 
что даже удобнее в случае больших приложений, но немного сложнее.
Поэтому celery мы рассмотрим в следующих уроках.

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

[//]: # (TODO route)

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

[//]: # (TODO синглтон для планировщика, вынесение его методов в слой scheduler)

[//]: # (TODO через lifespan)

[//]: # (TODO через добавление джобов по ходу дела через ручки)

[//]: # (TODO через декораторы)

[//]: # (TODO редисню подрубить, чтоб на несколько воркеров/нод можно было шарить задачи)

Подробнее см. 
https://apscheduler.readthedocs.io/en/stable/userguide.html
