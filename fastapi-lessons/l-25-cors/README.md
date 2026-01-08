# CORS (Cross‑Origin Resource Sharing)

Браузерные приложения (фронт) могут получать информацию не ото всех источников.
По умолчанию браузеры следуют политике одинакового источника (Same‑Origin Policy).
Благодаря этой политике скрипты с одного адреса (например https://address-frontend.com) 
не могут получать информацию только с этого адреса, 
те запросы на другие адреса (например https://address-backend.com) не будут проходить, 
выдавая ошибку.
Такая политика необходима для того, 
чтобы злоумышленники не могли отправлять запросы на одни сайты под видом других, кражи cookies итд.

Однако это может нам помещать в разработке своего приложения, 
ведь мы как минимум порой хотим:
- интегрироваться со сторонними сервисами
- подгружать какие-то данных со своих же сервисов, висящих на разных адресах
- порой просто упростить жизнь себе при локальном запуске приложения

## Для начала создадим простое backend приложение

Допустим у нас есть простое бэкенд приложение, 
которое будет иметь лишь одну ручку.
Конфиг этого приложения в **api/src/config.py** будет следующий:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='.env'
    )
    BASE_ROUTE_PATH: str = '/api/v1'

settings = Settings()
```

А сама логика в **api/src/main.py** будет следующая: 
```python
import uvicorn
from fastapi import FastAPI, HTTPException

from src.config import settings

app = FastAPI(
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs",
)


@app.get('/some-endpoint')
def semo_func():
    return 'Some response!'


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
```

## Запросы с frontend приложения

Чтобы удобнее было показывать как это все работает, 
в данном уроке есть простенькое frontend приложение, 
которое можно запустить в docker контейнере.

Для этого в папке **web_page** необходимо создать docker образ этого приложения:
```shell
docker build -t test_web_page_for_l_25_fastapi .
```
Затем его можно будет запустить на порту 12345:
```shell
docker run -p 12345:80 -d test_web_page_for_l_25_fastapi
```
Убедиться в том, что приложение запустилось можно будет при помощи команды:
```shell
docker ps
```
Она должна будет выдать что-то вроде:
```
CONTAINER ID   IMAGE                            COMMAND                  CREATED          STATUS          PORTS                                     NAMES
47cb10576ef8   test_web_page_for_l_25_fastapi   "/docker-entrypoint.…"   2 seconds ago    Up 2 seconds    0.0.0.0:12345->80/tcp, :::12345->80/tcp   magical_elion
```

После запуска приложения можно будет открыть его в браузере по адресу:
http://127.0.0.1:12345.

В интерфейсе этого приложения можно будет отправить GET запрос 
по адресу http://127.0.0.1:8000/some-endpoint.

Однако сейчас нам будет вылетать CORS ошибка.
В какой момент она появляется?

В момент запроса клиента браузер добавляет к запросу заголовок:
```
Origin: http://127.0.0.1:12345
```

Бэекенд же при обработке запроса может вернуть заголовок, 
в котором говориться кому разрешен доступ к ресурсу.
Этот ответный заголовок может выглядеть следующим образом:
```
Access-Control-Allow-Origin: http://127.0.0.1:12345
```
или же например разрешение для всех адресов:
```
Access-Control-Allow-Origin: *
```

Также в ответе могут приходить и заголовки разрешающие конкретные параметры запроса:
- **Access-Control-Allow-Origin** - домены, которым разрешён доступ
- **Access-Control-Allow-Methods** - разрешённые HTTP‑методы (GET, POST, PUT и др.)
- **Access-Control-Allow-Headers** - разрешённые заголовки в запросе
- **Access-Control-Max-Age** - время кэширования результатов preflight‑запроса
- **Access-Control-Allow-Credentials** - разрешает ли сервер отправку куки/авторизации

Чтобы разрешать браузеру отправлять запросы с определенного адреса, 
для начала зададим этот адрес как настройку в конфиге **фзш.ыкс.сщташпюзн**.
Тогда он будет выглядеть следующим образом:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='.env'
    )
    BASE_ROUTE_PATH: str = '/api/v1'
    ALLOWED_ORIGIN: str = ''


settings = Settings()
```

Теперь добавим в **api/src/config.py** middleware для добавление CORS хэдеров в ответы нашего приложения:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.ALLOWED_ORIGIN],
    allow_methods=['GET', 'POST'],
    allow_headers=['*']
)
```
Здесь используется стандартный модуль fastapi для обработки хедеров CORS, 
в котором мы можем давать разрешения на определенные 
хэдеры запросов, типы запросов, адрес клиентов (задаем из конфига) итд.
При этом мы можем как перечислять разрешаемые сущности, 
так и написать '*', чтобы сразу разрешить все.

Теперь если мы посмотрим в браузере адрес, 
на котором запустился наш фронтенд (допустим это 127.0.0.1:80), 
мы сможем добавить его в **api/.env** в разрешенные адреса:
```
ALLOWED_ORIGIN="http://127.0.0.1:12345"
```

Теперь запросы с фронтенда будут спокойна проходить на наш бэкенд, 
поскольку тот будет добавлять в ответ заголовок, 
указанный в настройках бэкенда.

Стоит напомнить, что для безопасности не рекомендуется давать разрешение 
на дополнительные адреса без необходимости.
Например те же фронтенд и бэкенд на проде могут быть развернуты на одном адресе, 
тогда в дополнительном настраивании CORS на проде не будет необходимости.
