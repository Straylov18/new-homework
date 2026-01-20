# Mock тесты

Порой легче не воспроизводить во время теста полный процесс работы приложения, 
а просто заменить нужный кусок приложения заглушкой.

Для таких ситуаций существует механизм моков.
**Мокирование** - это временная замена какой-то сущности при вызове ее их конкретного места кода.
Делается это зачастую для того, чтобы отвязать приложение от внешних сервисов, 
упростив таким образом логику работы приложения.
Мокировать можно объекты, функции, итд.

## Пример приложения с двумя сервисами на бэкенде

Допустим, что у нашего приложения есть два бэкенда: основной и сервис авторизации.
Сервис авторизации будет отвечать за вход в наше приложение.
Основной бекенд же будет делать запросы к сервису авторизации в моменты, 
когда пользователь должен залогиниться.

Чтобы им легче было обмениваться информаций, 
часть схем у них будет одинаковая, 
и таким образом они оба будут знать, 
в каком формате они должны обмениваться данными.

В нашем случае мы просто для простоты перекопируем эти схемы руками.
В больших же приложениях принято описывать их где-то в одном месте (или генерировать), 
а потом автоматически копировать во все модули при сборке приложения.
Такое общее для нескольких модулей приложения описание передаваемых данных называется **контрактом**.
Контрактом могут быть связаны как несколько бэкендов, так и бэкенд с фронтендом.
В случае использования разных языков программирования в разных модулях приложения 
генерацию осуществляют с помощью специальных библиотек, парсящих OpenAPI схему.

### Сервис авторизации

Для начала сделаем сервис, 
который будет эмулировать сервис авторизации.

У него будут схемы для передачи информации о пользователях в **api2/src/scheme.py**:
```python
from pydantic import BaseModel, Field

class User(BaseModel):
    email: str | None = Field(description="Email", default=None)
    password: str | None = Field(description="Password", default=None)
```

Пусть ручки для манипуляций с пользователями будут описаны в **api2/src/router.py** 
и будут выглядеть следующим образом:
```python
from fastapi import APIRouter, HTTPException

from src.scheme import User

router = APIRouter()

users = [User(email='qwe@mail.com', password='11')]


@router.post('/create-user')
async def create_user(body: User):
    for u in users:
        if u.email == body.email:
            raise HTTPException(status_code=400, detail="User with such email already exists!")
    users.append(body)
    return 'user created'


@router.post('/login')
async def login(body: User):
    for u in users:
        if u.email == body.email and u.password == body.password:
            return 'login succeeded'
    raise HTTPException(status_code=401, detail="Incorrect user name or password!")
```

Подключаться же все будет классическим образом в **api2/src/main.py**:
```python
import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

from src.config import settings
from src.router import router as user_router

app = FastAPI(
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs",
)

router = APIRouter(prefix=settings.BASE_ROUTE_PATH)

router.include_router(user_router, prefix='/user', tags=['user'])

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8001,
        reload=True,
    )
```

Его мы будем запускать на отдельном порту рядом с основным приложением:
```shell
poetry run uvicorn src.main:app --port 8001 --reload
```

### Основной сервис

Поскольку основной сервис должен будет ссылаться на сервис авторизации, 
мы должны прописать в конфигах адрес к нему.
Тогда наш **api1/src/config.py** будет выглядеть так:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='.env'
    )
    BASE_ROUTE_PATH: str = '/api/v1'
    AUTH_SERVER_ADDRESS: str = 'http://127.0.0.1:8001/api/v1'


settings = Settings()
```

Как мы и оговорили выше, в основном сервисе будут использоваться те же схемы.

Пусть основное приложение будет иметь только две ручки:
- одна будет логинить пользователя через сервис авторизации
- вторая будет выдавать информацию о последних успешных логинах

Тогда описание ручек в **api1/src/route/some_router.py** будет выглядеть так:
```python
from fastapi import APIRouter

from src.scheme.user import User
from src.service.some_service import get_successful_logins, login_user

router = APIRouter()


@router.post('/login')
async def login(body: User):
    return login_user(body)


@router.get('/list-successful-logins')
async def get_logins_info() -> list[User]:
    return get_successful_logins()
```

Опишем в сервисе **api1/src/service/some_service.py** взаимодействие с другим модулем:
```python
import httpx
from fastapi import HTTPException

from src.config import settings
from src.scheme.user import User

successful_logins: list[User] = []


def try_login_in_auth_server(user: User) -> bool:
    r = httpx.post(f'{settings.AUTH_SERVER_ADDRESS}/user/login', json=user.model_dump())
    if r.json() == 'login succeeded':
        return True
    return False


def login_user(user: User):
    if try_login_in_auth_server(user):
        successful_logins.append(user)
        return 'Залогинились через отдельностоящий сервис'
    else:
        raise HTTPException(status_code=400, detail="Не получилось войти через отдельностоящий сервис!")


def get_successful_logins() -> list[User]:
    return successful_logins
```
Здесь запросы ко второму сервису мы делаем с помощью библиотеки httpx 
(встроена в библиотеку starlette, на основе которой сделан fastapi).

## Тесты

Для сервиса авторизации можно написать обычные тесты, 
поскольку он в данном случае не ссылается ни на какие сторонние сервисы.

### Тесты для основного приложения

При вызове ручек основного приложения оно дергает ручки сервиса авторизации.
Таким образом при стандартной конфигурации без сервиса авторизации оно не сможет работать.

Однако запускать оба приложения для прогона тестов достаточно тяжело, 
плюс это очень сильно усложняет логику тестирования, и в ней тогда легче допустить ошибки.
А нам хорошо бы сделать тесты, которые будут проверять только логику работы основного сервиса. 
Ведь для сервиса авторизации мы можем написать свои отдельные тесты, которые будут проверять логику его работы.

То же мы можем делать при тестировании методом, использующих БД.

Для использования моков при написании тестов нам необходимо установить библиотеку **pytest-mock**:
```shell
poetry add pytest-mock --group test
```

[//]: # (TODO)

Подробнее о функционале библиотеки pytest-mock можно прочитать тут:
https://pytest-mock.readthedocs.io/en/latest/.
