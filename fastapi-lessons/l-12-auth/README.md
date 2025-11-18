# Авторизация в backend приложении

[//]: # (TODO Аутентификация, Авторизация)

## Виды аутентификации

При успешной аутентификации пользователь должен получить некий ключ, 
при помощи которого он будет подтверждать, 
что это собственно он, а не кто-то другой.

Существует два способа передачи такой информации:
- выдача бэкендом id сессии
- выдача бэкендом jwt токена

### Сессии

В случае реализации механизма сессий:
- бэкенд записывает у себя в БД информацию о том, кто залогинелся и в какое время (создает сессию) и выдает этой записи id (session_id)
- пользователь получает id сессии в ответе на запрос и хранит у себя
- теперь при каждом запросе пользователь будет прикреплять этот id сессии, 
и бэкенд будет проверять может ли пользователь делать те или иные действия

### JWT

В случае использования jwt токена:
- бэкенд шифрует сообщение, содержащее информацию о пользователе и времени логина, 
при помощи секретного ключа (который знает только бэкенд)
- пользователь получает jwt токен в ответе на запрос и хранит у себя
- теперь при каждом запросе пользователь будет прикреплять этот id сессии, 
и бэкенд будет расшифровывать этот токен при помощи секретного ключа (того же, которым и шифровал), 
чтобы достать информацию о пользователе и сессии из этого jwt токена

Те. в случае session_id информация о сессии храниться на бэкенде, 
а в случае jwt токена - на фронтенде.

При использовании jwt токена стоит помнить:

- что не стоит класть в jwt токен много данных в приложениях с большой нагрузкой, 
поскольку в нем при большой нагрузке она будет передавать для каждого запроса.

- не так удобно разлогинивать другое устройство, 
в отличие от случая, когда используются сессии (поскольку токен лежит у пользователя в браузере).

Мы в рамках данного урока будем использовать именно jwt токены, так как они удобнее для старта.

## Типы передачи токенов (или идентификаторов сессий)

Токен или идентификатор сессии принято передавать в запросе одним из двух способов:
- в хэдерах запроса
- в cookies запроса

### Передача токена в хедере запроса

[//]: # (TODO )
Не так удобно, поскольку придется подпихивать к каждому запросу.

### Передача токена в cookies запроса

Данные, которые каждый раз должны передаваться с фронтенда на бэкенд, 
удобнее всего хранить в cookie.
При запросах к бэку cookies автоматически подсовываются к каждому запросу.

Более того, сам бэк может добавлять новые cookie и убирать ненужных.

Однако если планируется создавать еще и десктопный или мобильный клиент приложения, 
данный способ не подходит, 
поскольку cookies поддерживаются только браузерами.

## FastAPI приложение обрабатывающее jwt токены в cookies запросов

Чтобы обрабатывать jwt токены в нашем бэкенд приложении, 
у нас должен быть секретный ключ, 
которым мы будем шифровать и расшифровывать все jwt токены.

Зададим его в конфиге (файле **src/config.py**):
```python
from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='.env'
    )
    BASE_ROUTE_PATH: str = '/api/v1'
    SECRET_KEY: str = '/api/v1'


settings = Settings()
```

Теперь опишем методы для работы с jwt токенами.
Делать мы это будем в отдельном файле **src/auth.py**.

Опишем метод создания jwt токена:
```python
import jwt
from datetime import datetime, timedelta, timezone

from src.config import settings

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm='HS256')
    return encode_jwt
```
Здесь:
- создается копия данных, которые будут записаны в jwt токен (```to_encode = data.copy()```)
- вычисляется дата, когда токен должен просрочиться 
(в данном случае через неделю: ```expire = datetime.now(timezone.utc) + timedelta(days=7)```)
- данные о сроке действия токена добавляются в данные, которые потом будем загружать в токен 
(```to_encode.update({"exp": expire})```)
- при помощи секретного ключа кодируется информация в jwt токен при помощи указанного алгоритма 'HS256'
(```encode_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm='HS256')```)

Добавим также метод, который будет проверять валидность jwt токена, 
и выдавать нам его содержимое, если он валиден:
```python
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
- токен декодируется при помощи секретного ключа из настроек приложения при помощи указанного алгоритма 'HS256' 
(```jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')```)
- у словаря декодированного токена смотрится дата окончания его срока годности 
(```expire: str = payload.get('exp')```)
- дата окончания срока годности приводится к текущему часовому поясу
(```expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)```
- проверяется просрочен ли токен
(```if (not expire) or (expire_time < datetime.now(timezone.utc)):```)
- в случае успеха возвращается полученная из токена информация

Также добавим метод, который будет непосредственно вытягивать jwt токен 
из cookies входящего запроса:
```python
from fastapi import Request, HTTPException

def get_token(request: Request):
    token = request.cookies.get('access_token')
    if not token:
        raise HTTPException(403, "нету токена")
    return token
```
Здесь:
- на вход приходит объект запроса (```request: Request```), 
который будет автоматически получаться в функции обработки роута 
от FastAPI при обработке REST запроса.
- из cookies запроса вытягивается токен по ключу 'access_token' (```request.cookies.get('access_token')```) 

Добавим описание роута для входа в систему (получения jwt токена):
```python
import uvicorn
from fastapi import FastAPI, Response, HTTPException, Depends
from fastapi.routing import APIRouter
from pydantic import EmailStr

from src.auth import create_access_token, get_token, get_token_payload_if_valid

BASE_ROUTE_PATH = "/api/v1"

app = FastAPI(
    openapi_url=f"{BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{BASE_ROUTE_PATH}/docs",
)

router = APIRouter(prefix=BASE_ROUTE_PATH)

users = [
    {
        'id': 0,
        'email': 'shaytan@cheburnetomail.ru',
        'password': '1',
    },
    {
        'id': 1,
        'email': 'admin@cheburnetomail.ru',
        'password': '1235',
    },
]


@router.get('/login')
async def login(email: EmailStr, password: str, response: Response):
    for u in users:
        if u["email"] == email and u["password"] == password:
            jwt_token_data = {"email": email}
            jwt_token = create_access_token(jwt_token_data)
            response.set_cookie("access_token", jwt_token)
            return "Успешный вход!"
    return "Пользователь не найден:("


app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
```
Здесь:
- описана импровизированная база данных пользователей (переменная users)
- ручка '/login', которая принимает на вход логин (email) и пароль. 
В ней также в параметрах передается response, 
к которому будет прикрепляться cookie с jwt токеном.
- при логине мы проверяем есть ли такой пользователь, 
и совпадает ли его логин и пароль с введенным
- мы создаем данные, 
которые запишутся в jwt токен (помимо срока его действия и дефолтных), 
в нашем случае это просто email (```{"email": email}```)
- создаем jwt токен при помощи нашей функции из **src/auth.py** (```jwt_token = create_access_token(jwt_token_data)```)
- прикрепляем cookie к ответу запроса (```response.set_cookie("access_token", jwt_token)```), 
чтобы эта cookie записалась в браузере пользователя 
и все время прикреплялась к запросам пользователя

Для выхода пользователя из аккаунта нужно всего лишь убрать jwt токен из его cookie:
```python
@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie(key="access_token")
    return {'message': 'Пользователь вышел из системы. Бб, дружище!'}
```

Если же мы теперь хотим в какой-то ручке проверить, 
что наш пользователь успешно вошел (ну и получить прочую информацию о нем), 
можно прикрутить dependency injection для получения токена, 
которая будет вызывать описанную нами в **src/auth.py** функцию "get_token":
```python
@router.get('/hello')
async def hello_user(token: str = Depends(get_token)):
    payload = get_token_payload_if_valid(token)

    user_email: str = payload.get('email')
    if not user_email:
        raise HTTPException(403, "Нет такого пользователя! Обманщик!")

    return f"Hi, {payload.get('email')}!"
```
Здесь:
- получаем токен из cookie запроса при помощи нашего метода "get_token" (```token: str = Depends(get_token)```)
- мы проверяем правильность токена (```payload = get_token_payload_if_valid(token)```)
- получаем email пользователя прямо из jwt токена, 
чтобы потом его вывести обратно (```user_email: str = payload.get('email')```)

## Хранение паролей в хэшированом виде

[//]: # (TODO )
