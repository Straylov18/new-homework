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

from src.adapter.db.session import async_session_maker
from src.config import Settings, settings
from src.repository.user import UserRepository
from src.repository.user_post import UserPostRepository


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

Воспользуемся же нашими репозиториями, переписав прошлый урок с их использованием.

### Упрощения в слое роутеров

Теперь нам не нужно прокидывать сессии через dependency injection в роутерах.

Тогда **src/route/user.py** будет выглядеть:
```python
from fastapi import APIRouter, Depends

from src.scheme.user import UserFromDB
from src.service.user import UserService
from src.utils.auth import get_token

router = APIRouter()


@router.get('/list')
async def get_users_list(token: str = Depends(get_token)) -> list[UserFromDB]:
    return [u.serialize() for u in await UserService.get_users_list(token)]
```

Тогда **src/route/user_post.py** будет выглядеть:
```python
from fastapi import APIRouter

from src.scheme.user_post import UserPostCreate, UserPostFromDB
from src.service.user_post import UserPostService
from src.utils.auth import get_token

router = APIRouter()


@router.get('/list')
async def get_user_posts_list() -> list[UserPostFromDB]:
    return [up.serialize() for up in await UserPostService.get_user_posts_list()]


@router.post('/')
async def create_user_post(data: UserPostCreate,
                           token: str = Depends(get_token)) -> UserPostFromDB:
    new_user_post = await UserPostService.create_user_post(data, token)
    return new_user_post.serialize()
```

Тогда **src/route/auth.py** будет выглядеть:
```python
from fastapi import APIRouter, Response

from src.scheme.user import UserCreate, UserFromDB, UserLogin
from src.service.user import UserService

router = APIRouter()


@router.post('/register')
async def create_user(data: UserCreate) -> UserFromDB:
    new_user = await UserService.create_user(data)
    return new_user.serialize()


@router.post('/login')
async def login(body: UserLogin, response: Response) -> str:
    return await UserService.login(body, response)


@router.post("/logout")
async def logout(response: Response) -> str:
    return await UserService.logout(response)
```

### Вынесение логики общения с базой данных из других слоев

Теперь упростим все места, 
где мы обращались к базе данных.

Например, в **src/utils/auth.py** перепишем функцию ```authenticate_user```:
```python
async def authenticate_user(email: EmailStr, password: str) -> User:
    user = await repository_container.user_repository().get_one(email=email)
    if not user:
        raise HTTPException(404, "Нету такого пользователя!")
    if not user or verify_password(plain_password=password, hashed_password=user.password) is False:
        raise HTTPException(404, "А-а! Неверный пароль!")
    return user
```

Также у нас упростятся сервисы.

Так, сервис **src/service/user.py** будет теперь выглядеть:
```python
from fastapi import HTTPException, Response
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.user import User
from src.scheme.user import UserCreate, UserLogin
from src.utils.auth import (authenticate_user, create_access_token,
                            get_password_hash, get_token_payload_if_valid)


class UserService:

    @staticmethod
    async def create_user(data: UserCreate, db_session: AsyncSession) -> User:
        if await UserService.is_user_already_exists(data.email, db_session):
            raise HTTPException(400, "такой пользователь уже есть")
        new_user = User(**data.model_dump(exclude_unset=True))
        new_user.password = get_password_hash(new_user.password)
        new_user.is_admin = False
        db_session.add(new_user)
        await db_session.commit()
        return new_user

    @staticmethod
    async def is_user_already_exists(email: EmailStr, db_session: AsyncSession) -> bool:
        query = await db_session.execute(select(User).where(User.email == email))
        user = query.scalar_one_or_none()
        if not user:
            return False
        return True

    @staticmethod
    async def get_user_by_email(email: EmailStr, db_session: AsyncSession) -> User:
        query = await db_session.execute(select(User).where(User.email == email))
        user = query.scalar_one_or_none()
        if not user:
            raise HTTPException(404, "нету такого пользователя")
        return user

    @staticmethod
    async def get_users_list(token: str, db_session: AsyncSession) -> list[User]:
        token_payload = get_token_payload_if_valid(token)
        user = await UserService.get_user_by_email(token_payload['email'], db_session)
        if not user.is_admin:
            raise HTTPException(403, "просматривать список пользователей может только админ!")
        query_result = await db_session.execute(select(User))
        return query_result.scalars().all()

    @staticmethod
    async def login(body: UserLogin, response: Response, db_session: AsyncSession) -> str:
        await authenticate_user(body.email, body.password, db_session)  # will throw an exception on fail
        jwt_token_data = {"email": body.email}
        jwt_token = create_access_token(jwt_token_data)
        response.set_cookie("access_token", jwt_token)
        return "Успешный вход!"

    @staticmethod
    async def logout(response: Response) -> str:
        response.delete_cookie(key="access_token")
        return 'Пользователь вышел из системы. Бб, дружище!'
```

А сервис **src/service/user.py** будет теперь выглядеть:
```python
from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.user_post import UserPost
from src.scheme.user_post import UserPostCreate
from src.service.user import UserService
from src.utils.auth import get_token_payload_if_valid


class UserPostService:

    @staticmethod
    async def create_user_post(data: UserPostCreate, token: str, db_session: AsyncSession) -> UserPost:
        token_payload = get_token_payload_if_valid(token)
        user = await UserService.get_user_by_email(token_payload['email'], db_session)
        if user.uid != data.user_uid:
            raise HTTPException(400, "вам можно создавать только от своего имени!")
            # лучше конечно делать свои кастомные исключения на базе дефолтных и выносить их в отдельный слой
        new_user_post = UserPost(**data.model_dump(exclude_unset=True))
        db_session.add(new_user_post)
        await db_session.commit()
        return new_user_post

    @staticmethod
    async def get_user_post_by_uid(uid: UUID4, db_session: AsyncSession) -> UserPost:
        query = await db_session.execute(select(UserPost).where(UserPost.uid == uid))
        user_post = query.scalar_one_or_none()
        if not user_post:
            raise HTTPException(404, "нету такого поста")
        return user_post

    @staticmethod
    async def get_user_posts_list(db_session: AsyncSession) -> list[UserPost]:
        query_result = await db_session.execute(select(UserPost))
        return query_result.scalars().all()
```
