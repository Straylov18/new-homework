# In-memory базы данных на примере redis

Существует отдельных класс баз данных, 
которые хранят данные в оперативной памяти.
Поскольку в таком случае нет ограничений из-за операций чтения-записи данных на диск, 
запросы к ним обрабатываются очень быстро.

Такие базы данных используют для обработки больших нагрузок.
Порой такие базы данных могут быть использованы как замена классическим, 
а порой могут использоваться вместе с ними.
Например, при помощи таких баз данных можно кешировать долгие операции, 
чтобы не выполнять их повторно, а лишь запоминать результат операции на какое-то время.
В данном уроке мы рассмотрим in-memory базу данных redis, 
которая является пожалуй наиболее популярной in-memory базой данных на данный момент.

Стоит сказать, что кеширование может быть осуществлено и без записи в какую-либо базу данных, 
ведь кеширующее приложение может само писать в оперативную память.
Однако сторонняя база данных дает больше гибкости при обращении с кешем.
Так например redis помимо обработки всех данных в оперативной памяти дублирует все на диске.
Таким образом при резком перезапуске всего приложения кеш может быть восстановлен с диска.
Также использование БД для кеширования позволяет легче проводить диагностику состояния системы.
Ну и это не говоря уж о том, 
что при распределении нагрузки на несколько одинаковых узлов 
например того же бэкенда, 
узлы приложения смогут иметь общий кеш, что достаточно часто бывает необходимо.

## Когда же может потребоваться кеширование?

Кеширование на бэкенде может потребоваться например:
- для кеширования результатов долгих вычислений
- когда бэкенд делает запросы к другому сервису, 
можно кешировать результат такого запроса
- когда в системе большое количество пользователей и происходит существенная нагрузка на классическую БД 
(на тот же postgres), можно запоминать результаты самых частых запросов к БД, 
чтобы не нагружать ее лушний раз
- для кеширования собственно самих запросов к бэкенду (ответы самих ручек)
- для кеширования информации о клиентах, которые стучаться в бэк, 
например информацию для того же rate-limiting 
(как в уроке 24, там можно указать, чтобы данные о пользователях хранились в redis)

## Подключение Redis к бэкенд приложению

Допустим у нас стандартное fastapi приложение.

Добавим настройки подключения к redis в **src.config.py**
```python
from typing import Any

from pydantic import RedisDsn, field_validator
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


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='.env'
    )
    BASE_ROUTE_PATH: str = '/api/v1'
    REDIS: RedisSettings = RedisSettings()


settings = Settings()
```
Здесь мы аналогично конфигам postgres используем генерацию ссылки подключения к БД 
при помощи функционала библиотеки **pydantic**.

Для удобства сам redis мы будем в рамках данного урока запускать 
в докере при помощи bash скрипта **start_redis_in_docker.sh**.
Вольюм как всегда не прокидываем для докер контейнера, 
чтобы можно было чистить redis повторным запуском скрипта.

Опишем настройки для подключения к redis в **.env**:
```.env
REDIS_SERVER=localhost
REDIS_PORT=6380
REDIS_DB=0
REDIS_USER=default
REDIS_PASSWORD=master
```

Для работы с redis в python на данный момент зачастую используют библиотеку:
- redis

Мы будем использовать асинхронную версию, установим ее в проект:
```shell
poetry add redis
```

Для генерации сессий с redis создадим специальную функцию в adapter-слое 
в **src/adapter/redis.py**:
```python
import redis

from src.config import settings


async def get_redis_connection():
    redis_client = await redis.from_url(
        settings.REDIS.REDIS_URI,
        encoding="utf-8",
        decode_responses=True
    )
    try:
        yield redis_client
    finally:
        await redis_client.close()
```

Для еще большей скорости общения с redis, 
в библиотеке есть возможность создавать пул соединений (connection pooling), 
и переиспользовать соединения после старых запросов.
Это позволяет лишний раз не создавать новые соединения, 
однако пока мы можем ограничиться и такой реализацией.

## Кеширование ответов при помощи in-memory баз данных на примере Redis

Очень часто in-memory базы данных используют для кеширования результатов частых запросов, 
чтобы лишний раз не пересчитывать для них результат и выдавать клиенту ответы намного быстрее.

### Кеширование результата запроса с использованием redis

Предположим в **src/service/redis_operations_service.py** у нас есть какая-то функция, 
которая долго отрабатывает:
```python
from time import sleep

async def long_string_generation(id: str) -> str:
    print('generating new value')
    sleep(2)
    return f'string with id: {id}'
```

В реальном приложении это также может быть запрос к другому сервису, сложный запрос к БД итд. 

Ответ этой функции можно кешировать на какое-то время (а может и на постоянно), 
если мы знаем, что ее результат не меняется от параметров или не часто меняется во времени.

Так, мы можем написать другую функцию в **src/service/redis_operations_service.py**, 
которая будет сохранять в redis результат выполнения этой функции с текущим параметром в виде строки
(беря аргумент функции как ключ).
При этом если же в редисе уже есть результат выполнения этой функции с текущим аргументом, 
то будем выдавать этот результат.
Тогда функция будет выглядеть следующим образом:
```python
async def get_some_string(id, redis_session):
    cashed_value = await redis_session.get(id)
    if cashed_value is not None:
        return cashed_value

    new_value = await long_string_generation(id)
    await redis_session.set(id, new_value, 15)
    # to set expire time separetly
    # await redis_session.expire(id, 3)
    return new_value
```
Стоит заметить что здесь мы задаем значение так, 
чтобы оно жило в редисе лишь 15 секунд в строчке 
```await redis_session.set(id, new_value, 15)```.

Тогда пусть слой роутеров будет использовать именно этот метод в **src/route/redis_string.py**:
```python
@router.get('/some-data/{id}')
async def get_same_data(id: str, redis_session=Depends(get_redis_connection)) -> str:
    return await get_some_string(id, redis_session)
```

В redis естественно поддерживается полный набор операций с хранящимися строками 
(обновление, удаление, получение с фильтром по ключу итд.).

Напишем ручки для удаление конкретного кешированного значения 
и для получения списка всех кешированных значений в **src/route/redis_string.py**:
```python
@router.delete('/some-data/{id}/clear-cache/')
async def clear_same_data_cache(id: str, redis_session=Depends(get_redis_connection)) -> str:
    await delete_some_string_cache(id, redis_session)
    return f'deleted cache for string with id: {id}'

@router.get('/get-all-cache-with-prefix/{cache_key_prefix}')
async def get_all_cache_with_prefix(cache_key_prefix: str, redis_session=Depends(get_redis_connection)):
    return await filter_cache_by_prefix(cache_key_prefix, redis_session)
```

Сервисный слой для них будет выглядеть следующим образом:
```python
async def delete_some_string_cache(id, redis_session):
    await redis_session.delete(id)

async def filter_cache_by_prefix(cache_key_prefix, redis_session):
    return await redis_session.scan(match=f'{cache_key_prefix}*')
```

## Дополнительные типы данных в redis

Помимо строк в redis можно хранить и другие популярные типы данных 
(например хэштаблицы, сеты, листы итд.).

### Хэштаблицы

Достаточно часто в redis используют хэштаблицы, 
поскольку по одному ключу появляется возможность 
хранить сразу множество данных, к которым будет сохраняться быстрый доступ.

Добавим пару ручек для работы с хеш таблицами в **src/route/redis_hash_table.py**:
```python
from fastapi import APIRouter, Depends

from src.adapter.redis import get_redis_connection
from src.service.redis_operations_service import (add_value_to_hash_table,
                                                  get_all_hash_table_values)

router = APIRouter()


@router.get('/get-all-hash-table-values')
async def get_hash_table_values(redis_session=Depends(get_redis_connection)):
    return await get_all_hash_table_values(redis_session)


@router.post('/set-hash-table-value/{hkey}/{hvalue}')
async def set_hash_table_value(hkey: str, hvalue: str, redis_session=Depends(get_redis_connection)):
    return await add_value_to_hash_table(hkey, hvalue, redis_session)
```

В сервисном слое они могут обрабатываться следующим образом:
```python
HASH_TABLE_NAME = 'some_hash_table'

async def get_all_hash_table_values(redis_session):
    data = await redis_session.hgetall(HASH_TABLE_NAME)
    return data if data else None

async def add_value_to_hash_table(hkey, hvalue, redis_session):
    data = {}
    data[hkey] = hvalue
    await redis_session.hset(HASH_TABLE_NAME, mapping=data)
```

### Листы

Еще очень часто в redis используются листы.
С их помощью можно реализовывать например очереди задач для микросервисов.

В случае реализации очередей для микросервиса 
один микросервис может класть в очередь например какую-нибудь задачу, 
а второй вытягивать задачи, добавленные раньше всего, 
удаляя их при успешном выполнении.
Таким образом в листе всегда будут только актуальные задачи.

Напишем ручки для добавления элемента в лист 
и для вытягивания элемента с начала или с конца листа.

Ручки в **src/route/redis_list.py** могут выглядеть следующим образом:
```python
from fastapi import APIRouter, Depends

from src.adapter.redis import get_redis_connection
from src.service.redis_operations_service import (lpop_list_value,
                                                  push_value_to_list,
                                                  rpop_list_value)

router = APIRouter()


@router.get('/get-last-list-values')
async def get_last_list_value(redis_session=Depends(get_redis_connection)):
    return await lpop_list_value(redis_session)


@router.get('/get-first-list-values')
async def get_first_list_value(redis_session=Depends(get_redis_connection)):
    return await rpop_list_value(redis_session)


@router.post('/push-list-value/{value}')
async def push_list_value(value: str, redis_session=Depends(get_redis_connection)) -> int:
    return await push_value_to_list(value, redis_session)
```

Реализация же этих ручек пусть будет следующая:
```python
LIST_NAME = 'some_list'

async def lpop_list_value(redis_session):
    return await redis_session.lpop(LIST_NAME)

async def rpop_list_value(redis_session):
    return await redis_session.rpop(LIST_NAME)

async def push_value_to_list(value, redis_session):
    await redis_session.lpush(LIST_NAME, value)
    return await redis_session.llen(LIST_NAME)
```
Здесь команды ```lpop``` и ```rpop``` будут 
при получении элемента листа слева или справа сразу удалять его из редиса.

Больше информации о подключении redis в python приложение 
при помощи библиотеки redis можно почитать тут:
https://redis.readthedocs.io/en/stable/index.html.

Также в новых версиях redis есть механизмы брокера сообщений (Pub/Sub, stream).
Их мы рассмотрим в дальнейших уроках.
