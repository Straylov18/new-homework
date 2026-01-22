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

Пусть основное приложение будет иметь только три ручки:
- одна будет логинить пользователя через сервис авторизации
- вторая будет выдавать информацию о последних успешных логинах
- третья будет чистить информацию о последних успешных логах

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


@router.delete('/clear-login-logs')
async def clear_login_logs():
    return remove_successful_logins()
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


def remove_successful_logins():
    successful_logins.clear()
```
Здесь запросы ко второму сервису мы делаем с помощью библиотеки httpx 
(встроена в библиотеку starlette, на основе которой сделан fastapi).

Его мы будем запускать на другом порту (допустим на 8000):
```shell
poetry run uvicorn src.main:app --port 8000 --reload
```

## Тесты

Для сервиса авторизации можно написать обычные тесты, 
поскольку он в данном случае не ссылается ни на какие сторонние сервисы.

### Тесты для основного приложения

#### Фикстуры

Для начала сделаем фикстуры в **api1/tests/conftest.py**:
```python
import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def async_client():
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test'
    )


@pytest.fixture
def user_data_1():
    return {'email': 'first@mail.com', 'password': '1'}


@pytest.fixture
def user_data_2():
    return {'email': 'second@mail.com', 'password': '22'}


@pytest.fixture
def clear_login_logs(client):
    client.delete('/api/v1/some-router/clear-login-logs')
```
Здесь мы создаем:
- фикстуры клиентов для отправки запросов на наше приложение
- фикстуры данных пользователей (двух видов)
- фикстуру для отчистки логов успешных логинов приложения 
(Тут посредством дерганья ручки этого приложения. 
Но вообще если бы мы не хранили данные в оперативке, 
то лучше было бы просто питоновским кодом дернуть например запрос на удаление данных из БД, 
чтобы избавиться от лишнего усложнения тестов)

### Мокирование запросов к сервису авторизации

При вызове ручек основного приложения, оно дергает ручки сервиса авторизации.
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

Напишем тест на ручку логирования в **api1/tests/test_auth_server_integrations.py**:
```python
@pytest.mark.asyncio
async def test_login_succeeded(mocker, async_client, user_data_1):
    async with async_client as ac:
        mock_login = mocker.patch('src.service.some_service.httpx.post')
        mock_login.return_value.json.return_value = 'login succeeded'

        response = await ac.post('/api/v1/some-router/login', json=user_data_1)
        mock_login.assert_called_once_with(
            f'{settings.AUTH_SERVER_ADDRESS}/user/login',
            json=user_data_1
        )
        assert response.json() == 'Залогинились через отдельностоящий сервис'
        assert response.status_code == 200
```
Здесь:
- в сервисе ```src.service.some_service``` мокируем все ```httpx.post``` 
(при помощи команды ```mock_login = mocker.patch('src.service.some_service.httpx.post')```)
- мокируем возвращаемые функцией значения через ```.return_value``` 
(таким образом строчка ```mock_login.return_value.json.return_value = 'login succeeded'``` мокирует вывод ответа на запрос 
и мокирует вывод функции ```.json()``` на ```'login succeeded'```). 
Таким образом мы заменяем строчку из **api1/src/service/some_service.py** 
```r = httpx.post(f'{settings.AUTH_SERVER_ADDRESS}/user/login', json=user.model_dump())``` 
на ```r = 'login succeeded'```.
- потом мы в тесте делаем вызов и ожидаем, что наш вызов дернет нашу замокированную функцию
- мы можем также проверить, вызвалась ли наша замокированная функция с нужными параметрами при помощи 
```mock_login.assert_called_once_with(...)```

Напишем аналогичный тест на проверку неуспешной попытки логина:
```python
@pytest.mark.asyncio
async def test_login_failed(mocker, async_client, user_data_1):
    async with async_client as ac:
        mock_login = mocker.patch('src.service.some_service.httpx.post')
        mock_login.return_value.json.return_value = 'NOT succeeded (be-be he-he)'

        response = await ac.post('/api/v1/some-router/login', json=user_data_1)
        mock_login.assert_called_once_with(
            f'{settings.AUTH_SERVER_ADDRESS}/user/login',
            json=user_data_1
        )
        assert response.json() == {'detail': 'Не получилось войти через отдельностоящий сервис!'}
        assert response.status_code == 400
```
Здесь мы все также можем проверять, что запрос в сторонний сервис уходил.

Также проверим ручку получения логов, отчистив логи через фикстуру ```clear_login_logs```, 
после чего сделав пару успешных и неуспешный запросы логина к сервису:
```python
@pytest.mark.asyncio
async def test_login_counter(mocker, async_client, clear_login_logs, user_data_1, user_data_2):
    async with async_client as ac:
        mock_login = mocker.patch('src.service.some_service.httpx.post')
        mock_login.return_value.json.return_value = 'login succeeded'

        await ac.post('/api/v1/some-router/login', json=user_data_1)
        await ac.post('/api/v1/some-router/login', json=user_data_2)

        mock_login = mocker.patch('src.service.some_service.httpx.post')
        mock_login.return_value.json.return_value = 'login NOT succeeded (be-be he-he)'

        # не должно записывать в логи, потому что мы замокировали ошибку
        await ac.post('/api/v1/some-router/login', json=user_data_2)

        response = await ac.get('/api/v1/some-router/list-successful-logins')
        assert response.json() == [user_data_1, user_data_2]
        assert response.status_code == 200
```
Здесь мы несколько раз за тест мокируем ответ от сервиса авторизации, 
чтобы проверить лишь часть кода, отвечающую за запись логов.

Подробнее о функционале библиотеки pytest-mock можно прочитать тут:
https://pytest-mock.readthedocs.io/en/latest/.
