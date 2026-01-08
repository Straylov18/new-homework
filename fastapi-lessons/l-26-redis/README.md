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

Для работы с redis в python зачастую используют одну из двух библиотек:
- redis (синхронная)
- aioredis (асинхронная)

Мы будем использовать асинхронную версию, установим ее в проект:
```shell
poetry add aioredis
```

Для генерации сессий с redis создадим специальную функцию в adapter-слое 
в **src/adapter/redis.py**:
```python
import aioredis

from src.config import settings


async def get_redis_connection():
    redis = await aioredis.from_url(
        settings.REDIS.REDIS_URI,
        encoding="utf-8",
        decode_responses=True
    )
    try:
        yield redis
    finally:
        await redis.close()
```

Для еще большей скорости общения с redis, 
в библиотеке есть возможность создавать пул соединений (connection pooling), 
и переиспользовать соединения после старых запросов.
Это позволяет лишний раз не создавать новые соединения, 
однако пока мы можем ограничиться и такой реализацией.

## Кеширование ответов при помощи in-memory баз данных на примере Redis

[//]: # (TODO)

## Кеширование результата запроса с использованием redis

[//]: # (TODO)

## Дополнительные типы данных в redis

[//]: # (TODO hash, list, set, etc.)

Больше информации о подключений redis в python приложение 
при помощи aioredis можно почитать тут:
https://aioredis.readthedocs.io/en/v1.3.0/mixins.html.

## Pub/Sub, stream механизмы в Redis

[//]: # (TODO)
