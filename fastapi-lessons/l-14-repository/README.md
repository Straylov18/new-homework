# Более качественное описание запросов к базе данных

В прошлом уроке мы делали авторизацию пользователей с использованием базы данных.
Причем нам пришлось описывать запросы к базе данных как из сервисов, 
так и из **utils**, что не совсем удобно 
(особенно если учесть, что логика приложения будет становиться только сложнее со временем).
Чтобы придерживаться стратегии разнесения приложения на слои, 
достаточно часто описание запросов к базе данных выносят в слой **repository**.
Тогда когда нам нудно будет получить что-то из базы данных мы просто будем обращаться к этому слою.
Если сделать так, чтобы сессии генерировались в этом слое, 
нам даже не придется их прокидывать через все приложение.

## Слой repository

### Создание абстрактного repository класса

[//]: # (TODO)

```python
from abc import ABC, abstractmethod


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one():
        raise NotImplementedError

    @abstractmethod
    async def get_one():
        raise NotImplementedError

    @abstractmethod
    async def get_list():
        raise NotImplementedError
```

### Создание класса репозитория для общих операций с моделями

На основе абстрактного класса теперь можно создать шаблонный репозиторий 
для реализации CRUD при работе с моделями 
(в нашем случае будет не полный CRUD, а лишь часть для примера). 
Поэтому наш шаблонный репозиторий будет иметь поле модели, 
с помощью которой он будет осуществлять запросы к БД.

Поскольку для осуществления запросов к БД необходимо получения сессий, 
мы будем прокидывать в объект нашего шаблонного репозитория генератор сессий.

Тогда наш репозиторий будет выглядеть следующим образом:
```python
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyRepository(AbstractRepository):
    model = None

    def __init__(self, async_session_maker: AsyncSession):
        self.async_session_maker = async_session_maker

    async def add_one(self, data: dict):
        obj = self.model(**data)
        async with self.async_session_maker() as session:
            session.add(obj)
            await session.commit()
        return obj

    async def get_one(self, **filter_by):
        async with self.async_session_maker() as session:
            query = select(self.model).filter_by(**filter_by)
            res = await session.execute(query)
            res = res.scalar_one_or_none()
        return res

    async def get_list(self, **filter_by):
        async with self.async_session_maker() as session:
            query = select(self.model)
            res = await session.execute(query)
            res = [row[0] for row in res.all()]
        return res
```
Здесь мы можем написать наиболее общие параметры для операций с БД (например те же фильтры), 
чтобы в дальнейшем можно было просто унаследоваться от данного репозитория, 
и как можно меньше описывать заново.

### Репозитории для конкретных сущностей

Теперь на основе шаблонного репозитория можно очень просто создавать репозитории для работы с объектами нашей БД
(или нескольких шаблонных репозиториев, если нельзя все подпихнуть под один формат).
Для этого нужно будет просто задать дочернему репозиторию соответствующую модель.

Тогда репозиторий для работы с пользователями в **src/repository/user.py** будет выглядеть:
```python
from src.model.user import User
from src.utils.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    model = User
```

А репозиторий для работы с постами пользователей в **src/repository/user_post.py** будет выглядеть:
```python
from src.model.user_post import UserPost
from src.utils.repository import SQLAlchemyRepository


class UserPostRepository(SQLAlchemyRepository):
    model = UserPost
```

### Что мы таким образом получили?

Таким образом мы: 
- сильно сократили количество кода, необходимого для описания однотипных операций
- улучшили читаемость кода в сервисах
- избавились от спагетти кода
- (забегая вперед) сделали код более удобным для тестирования

## Слой container

Также в приложениях с большим количеством сущностей и слоев, 
достаточно часто можно встретить специальный слой контейнеров.
В нем мы можем объединять создание объектов, 
хранящих логику конкретного слоя.
Например, можно запихнуть фабрики создания всех репозиториев в контейнер репозиториев.
Тогда для получения любого репозитория в конкретном месте приложения 
можно будет просто импортировать контейнер репозиториев и вызвать нужный метод-генератор.

Тогда создадим контейнер репозиториев в файле **src/container/repository.py**:
```python
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.config import Settings, settings
from src.repository.user import UserRepository
from src.repository.user_post import UserPostRepository
from src.adapter.db.session import async_session_maker


@dataclass
class RepositoryContainer:
    settings: Settings
    async_session_maker: async_sessionmaker[AsyncSession]

    def user_repository(self) -> UserRepository:
        return UserRepository(async_session_maker=self.async_session_maker)

    def user_post_repository(self) -> UserPostRepository:
        return UserPostRepository(async_session_maker=self.async_session_maker)


repository_container = RepositoryContainer(settings=settings, async_session_maker=async_session_maker)
```
Здесь методы ```user_repository``` и ```user_post_repository``` 
будут создавать соответствующие репозитории с заданными генераторами сессий.

Тогда нам вообще не придется прокидывать ни сессии, ни их генераторы нигде в коде.

## Описание бизнес логики при помощи репозиториев

[//]: # (TODO вынесение из сервисов и из utils/auth.py)

[//]: # (TODO не нужно еперь прокидывать DI сессий из роутеров)
