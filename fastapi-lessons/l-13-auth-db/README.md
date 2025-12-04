# Авторизация на примере приложения с базой данных

В данном уроке мы рассмотрим безопасный способ хранения паролей в базе данных.

## Скелет приложения

Для начала создадим скелет приложения, 
в котором пользователи смогут регистрироваться, логиниться и создавать посты.

Также сделаем в этой системе роль администратора, 
который сможет просматривать всех пользователей.

Все ручки можно будет разбить на три группы.
Тогда **main.py** будет выглядеть следующим образом:
```python
import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

from src.config import settings
from src.route.auth import router as auth_router
from src.route.user import router as user_router
from src.route.user_post import router as user_post_router

app = FastAPI(
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs",
)

router = APIRouter(prefix=settings.BASE_ROUTE_PATH)

router.include_router(auth_router, prefix='/auth', tags=['auth'])
router.include_router(user_router, prefix='/user', tags=['user'])
router.include_router(user_post_router, prefix='/user-post', tags=['user_post'])

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
```

Модель пользователя в **src/model/user.py** будет выглядеть следующим образом:
```python
import uuid

from sqlalchemy import UUID, Boolean, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.adapter.db.session import Base
from src.scheme.user import UserFromDB


class User(Base):
    __tablename__ = 'user'
    __table_args__ = (UniqueConstraint('email', name='_user_email'),)

    uid: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def serialize(self) -> UserFromDB:
        return UserFromDB(
            uid=self.uid,
            name=self.name,
            email=self.email,
            is_admin=self.is_admin,
        )
```

Модель поста пользователя в **src/model/user_post.py** будет выглядеть следующим образом:
```python
import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, UUID, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.adapter.db.session import Base
from src.scheme.user_post import UserPostFromDB


class UserPost(Base):
    __tablename__ = 'user_post'

    uid: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=True)
    date_created: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    user_uid: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("user.uid"), nullable=False)

    user = relationship("User", backref="user_posts")

    def serialize(self) -> UserPostFromDB:
        return UserPostFromDB(
            uid=self.uid,
            title=self.title,
            text=self.text,
            date_created=self.date_created,
            user_uid=self.user_uid,
        )
```

Опишем pydantic схемы пользователей в **src/scheme/user.py**:
```python
from pydantic import UUID4, BaseModel, Field


class UserCreate(BaseModel):
    name: str | None = Field(description="Name", default=None)
    email: str | None = Field(description="Email", default=None)
    password: str | None = Field(description="Password", default=None)


class UserLogin(BaseModel):
    email: str | None = Field(description="Email", default=None)
    password: str | None = Field(description="Password", default=None)


class UserFromDB(BaseModel):
    uid: UUID4 = Field(description="User uid")
    name: str | None = Field(description="Name", default=None)
    email: str | None = Field(description="Email", default=None)
    is_admin: bool = Field(description="Is this user admin or not", default=False)
```

Pydantic схема поста пользователя в **src/scheme/user_post.py** будет выглядеть:
```python
from pydantic import UUID4, BaseModel, Field


class UserPostCreate(BaseModel):
    title: str | None = Field(description="Post title", default="Post title")
    text: str | None = Field(description="Post text", default=None)
    user_uid: UUID4 = Field(description="User uid")


class UserPostFromDB(BaseModel):
    uid: UUID4 = Field(description="User post uid")
    title: str | None = Field(description="Post title", default="Post title")
    text: str | None = Field(description="Post text", default=None)
    user_uid: UUID4 = Field(description="User uid")
```

## Регистрация и логин

Для начала реализуем регистрацию и логин по аналогии с прошлым уроком.
Единственное отличие будет в том, 
что теперь мы будем пытать хранить пароли в защищенном виде в базе данных.

### Хранение паролей в базе данных и работа с ними

Чтобы в случае утечки базы данных пароли пользователей системы не утекли в сеть, 
их ни в коем случае нельзя хранить в открытом виде.

Чтобы пароли невозможно было вытянуть имея доступ к базе данных, 
их необходимо хранить в зашифрованном виде.
Чтобы операцию шифрования невозможно было провернуть вспять и получить исходные пароли, 
принято хранить в базе данных только их хэш.
Хэш функция - функция, преобразующая входные данные произвольного размера 
в выходную строку конкретного размера в соответствии с определённым алгоритмом.
Получается если операция хэширования необратима, 
даже имея хэши всех паролей, злоумышленник не сможет получить исходные пароли 
(это будет сделать очень-очень сложно).

Однако если у нескольких пользователей будут одинаковые пароли, 
то и хэши этих паролей будут одинаковые.
Получается если злоумышленник знает хэши всех паролей и знает пароли от некоторых пользователей 
(допустим украл из других систем, а пользователи используют одинаковые пароли везде .. уже стало страшно и ты пошел везде менять пароли?), 
то видя пароли с одинаковым хэшем он сразу узнает несколько паролей, 
если узнает хотя бы от одного из этих пользователей.

Чтобы это предотвратить придумали "солить" пароли, те. хэшировать не сам пароль, 
а пароль вместе с какими-то ненужными открыто хранящимися данными 
(например с точным временем создания хэша).
Тогда в базе данных пароль будет храниться как "соль" в открытом виде + хэш пароля, 
и для сравнения введенного пользователем пароля хэш будет браться от пароля с солью из базы данных.

### Работа с хэшами паролей на практике с помощью Argon2id

Для правильного хранения паролей написано много библиотек, 
поэтому нет необходимости реализовывать все механизму вручную.

На данный момент для хэширования паролей принято использовать библиотеку argon2, 
установим ее:
```shell
poetry add argon2-cffi
```

Для дальнейшего использования операций хэширования и проверки пароля 
добавим пару методов в файл **src/utils/auth.py** к прошлому уроку:
```python
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import HTTPException, Request
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.model.user import User

password_hasher = PasswordHasher()


def get_password_hash(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        password_hasher.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False


async def authenticate_user(email: EmailStr, password: str, db_session: AsyncSession) -> User:
    query = await db_session.execute(select(User).where(User.email == email))
    user = query.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Нету такого пользователя!")
    if not user or verify_password(plain_password=password, hashed_password=user.password) is False:
        raise HTTPException(404, "А-а! Неверный пароль!")
    return user


def get_token(request: Request):
    token = request.cookies.get('access_token')
    if not token:
        raise HTTPException(403, "нету токена")
    return token


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm='HS256')
    return encode_jwt


def get_token_payload_if_valid(token) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
    except jwt.InvalidTokenError:
        raise HTTPException(403, "Нет валидного jwt токена!")

    expire: str = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        raise HTTPException(403, "jwt токен просрочился")

    return payload
```
Здесь:
- ```get_password_hash(password: str) -> str:``` - 
генерирует хэш пароля
- ```verify_password(plain_password: str, hashed_password: str) -> bool:``` - 
проверяет, что сгенерированный хэш пароля соответствует проверяемому паролю
- ```authenticate_user(email: EmailStr, password: str, db_session: AsyncSession) -> User:``` - 
возвращает пользователя, если пароль логин и пароль верны
- ```get_token```, ```create_access_token```, ```get_token_payload_if_valid``` - 
функции для работы с jwt токеном из предыдущего урока

Сервис же пользователя **src/service/user.py**, реализующий операции с ним, 
будет выглядеть тогда следующим образом:
```python
from fastapi import HTTPException, Response
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.user import User
from src.scheme.user import UserCreate, UserLogin
from src.utils.auth import (authenticate_user, create_access_token,
                            get_password_hash)


class UserService:

    @staticmethod
    async def create_user(data: UserCreate, db_session: AsyncSession) -> User:
        if await UserService.is_user_already_exists(data.email, db_session):
            raise  HTTPException(400, "такой пользователь уже есть")
        new_user = User(**data.model_dump(exclude_unset=True))
        new_user.password = get_password_hash(new_user.password)
        new_user.is_admin = False
        db_session.add(new_user)
        await db_session.commit()
        await db_session.refresh(new_user)
        return new_user

    @staticmethod
    async def is_user_already_exists(email: EmailStr, db_session: AsyncSession) -> bool:
        query = await db_session.execute(select(User).where(User.email == email))
        user = query.scalar_one_or_none()
        if not user:
            return False
        return True

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

Таким образом благодаря использованию библиотеки argon2 все пароли пользователя будут генерироваться в хэшированном виде, 
более того каждый раз хэш от одного и того же пароля будет генерироваться по-разному.

О рекомендованных методах хранения паролей можно прочитать тут:
https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html.

## Repository слой

[//]: # (TODO перед тестированиями надо рассказать про этот слой, чтоб мокать потом удобнее было)

## Проверка данных при обработке запросов

[//]: # (TODO)

## Создание базового админа

[//]: # (TODO создание admin пользователя в миграциях)
