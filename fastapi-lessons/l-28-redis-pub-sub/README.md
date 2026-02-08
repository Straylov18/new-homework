# Pub/Sub (Publisher/Subscriber) механизм в redis

Порой возникает задача осуществить обмен событиями между множеством разных микросервисов.

Для подобных задач часто используют pub/sub (Publisher/Subscriber) механизмы, 
для массовой отправки и получения данных.

Принцип работы pub/sub:
- Сервис-издатель (публикатор) отправляет сообщения в канал
- Подписанные на этот канал сервисы-подписчики, получают опубликованные сообщения.
- Сервисы-подписчики получают только сообщения, 
опубликованные в каналы, на которые они подписаны.

При реализации такого механизма подписчики могут не знать, 
сколько издателей существует, 
а издатели могут не знать, сколько подписчиков получают их сообщения.
Подобная реализация pub/sub есть и в redis.
Если издатель отправил сообщение и на канал никто не был подписан, 
то сообщение просто потеряется 
(если необходимо удостовериться, что сообщение было отработано, 
в redis есть механизм stream, о котором будет рассказано в дальнейших уроках).

Также подобные механизмы используются для написания чат приложений 
или отправки уведомлений в реальном времени.

## Publisher

Для начала сделаем сервис публикации сообщений в очередь, 
чтобы при REST запросе на ручку он отправлял сообщение в указанную очередь.
Опишем это все в **api_publisher/main.py**:
```python
import uvicorn
from fastapi import Depends, FastAPI

from src.adapter.redis import get_redis_connection
from src.config import settings

app = FastAPI(
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs",
)


@app.get('/publish/{channel}')
async def publish_message(channel: str, message: str, redis_session=Depends(get_redis_connection)) -> str:
    await redis_session.publish(channel, message)
    return f"Published: {message}"


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
```
Здесь командой ```await redis_session.publish(channel, message)``` 
происходит публикация сообщения в очередь redis.

## Subscriber

Теперь создадим сервис, который будет при старте подписываться на указанное канал.
Пусть этот сервис будет просто выводить сообщения, 
которые приходят в указанный канал.
Чтобы мы могли запускать несколько разных подписчиков разных каналов, 
мы будем получать название канала из переменных окружения при запуске.

В конфиге зададим ему настройку, 
которая будет определять к какому каналу редиса он должен будет подключаться.
Пусть класс настроек в **spi_subscriber/src/config.py** 
будет выглядеть следующим образом: 
```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='.env'
    )
    CHANNEL_NAME: str = 'bimba'
    REDIS: RedisSettings = RedisSettings()
```

Сами же обработки сообщений из потока опишем в **spi_subscriber/src/main.py**:
```python
import asyncio
import time

from adapter.redis import get_redis_connection
from config import settings


async def subscribe_channel():
    redis_session = await get_redis_connection()
    pubsub = redis_session.pubsub()
    await pubsub.subscribe(settings.CHANNEL_NAME)

    print(f'Subscribed to "{settings.CHANNEL_NAME}" channel.')

    while True:
        message = await pubsub.get_message()
        if message and not message['type'] == 'subscribe':
            print(f"Received: {message['data']}")
        time.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(subscribe_channel())
```
Здесь мы:
- начинаем слушать сообщения для указанного канала:
    ```python
    redis_session = await get_redis_connection()
    pubsub = redis_session.pubsub()
    await pubsub.subscribe(settings.CHANNEL_NAME)
    ```
- начинаем бесконечно проверять канал на получение новых сообщений:
    ```python
    while True:
    message = await pubsub.get_message()
    if message and not message['type'] == 'subscribe':
    print(f"Received: {message['data']}")
    time.sleep(0.1)
    ```

## Запуск через docker-compose.yml

Чтобы пронаблюдать, 
что сообщения доходят сразу до нескольких слушателей одного и того же канала, 
необходимо будет развернуть несколько одинаковых модулей слушателей с разными настройками.
Напишем Docker файлы для более удобного запуска множества одинаковых модулей.

Для публикатора сообщений **api_publishe/Dockerfile** 
будет выглядеть следующим образом:  
```dockerfile
FROM python:3.12-slim

WORKDIR /usr/src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH .

RUN set -xe \
    && apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && pip install virtualenvwrapper poetry==1.8.2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

ADD ./src ./src

EXPOSE 8000

CMD poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Для обработчиков сообщений (подписчиков) **api_subscriber/Dockerfile** 
будет выглядеть следующим образом:  
```dockerfile
FROM python:3.12-slim

WORKDIR /usr/src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH .

RUN set -xe \
    && apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && pip install virtualenvwrapper poetry==1.8.2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

ADD ./src ./src

EXPOSE 8000

ARG CHANNEL_NAME
ENV CHANNEL_NAME=${CHANNEL_NAME}

CMD poetry run python3 src/main.py
```

Теперь чтобы удобно запускать сразу много сервисов, напишем **docker-compose.yml**.
Он будет выглядеть следующим образом:
```yml
---
services:

  publisher:
    build:
      context: api_publisher
    container_name: publisher
    environment:
      BASE_ROUTE_PATH: ${BASE_ROUTE_PATH-/api/v1}
      REDIS_SERVER: $REDIS_SERVER
      REDIS_PORT: $REDIS_PORT
      REDIS_DB: $REDIS_DB
      REDIS_USER: $REDIS_USER
      REDIS_PASSWORD: $REDIS_PASSWORD
    ports:
      - "${API_EXTERNAL_PORT-8000}:8000"
    networks:
      - redis-pub-sub
    depends_on:
      redis-db:
        condition: service_healthy

  subscriber1:
    build:
      context: api_subscriber
    container_name: subscriber1
    environment:
      CHANNEL_NAME: "bimba"
      REDIS_SERVER: $REDIS_SERVER
      REDIS_PORT: $REDIS_PORT
      REDIS_DB: $REDIS_DB
      REDIS_USER: $REDIS_USER
      REDIS_PASSWORD: $REDIS_PASSWORD
    networks:
      - redis-pub-sub
    depends_on:
      redis-db:
        condition: service_healthy

  subscriber2:
    build:
      context: api_subscriber
    container_name: subscriber2
    environment:
      CHANNEL_NAME: "bimba"
      REDIS_SERVER: $REDIS_SERVER
      REDIS_PORT: $REDIS_PORT
      REDIS_DB: $REDIS_DB
      REDIS_USER: $REDIS_USER
      REDIS_PASSWORD: $REDIS_PASSWORD
    networks:
      - redis-pub-sub
    depends_on:
      redis-db:
        condition: service_healthy

  subscriber3:
    build:
      context: api_subscriber
    container_name: subscriber3
    environment:
      CHANNEL_NAME: "bumba"
      REDIS_SERVER: $REDIS_SERVER
      REDIS_PORT: $REDIS_PORT
      REDIS_DB: $REDIS_DB
      REDIS_USER: $REDIS_USER
      REDIS_PASSWORD: $REDIS_PASSWORD
    networks:
      - redis-pub-sub
    depends_on:
      redis-db:
        condition: service_healthy

  redis-db:
    image: "redis:8"
    container_name: redis-db
    environment:
      REDIS_USER_PASSWORD: $REDIS_PASSWORD
    networks:
      - redis-pub-sub
    ports:
      - "${REDIS_EXTERNAL_PORT-6380}:6379"
    healthcheck:
      test: [ "CMD", "redis-cli", "-a", "$REDIS_PASSWORD", "ping" ]
      interval: 2s
      timeout: 5s
      retries: 5
    restart: unless-stopped

networks:
  redis-pub-sub:
```
Здесь есть:
- один ```publisher``` контейнер, 
с которого мы будем отправлять сообщения
- три контейнера подписчиков 
  - ```subscriber1``` (подписан на канал **bimba**)
  - ```subscriber2``` (подписан на канал **bimba**)
  - ```subscriber3``` (подписан на канал **bumba**)
- контейнер с редисом ```redis-db```

Все эти контейнеры объединены в общую сеть ```redis-pub-sub```.
Контейнеры, зависящие от контейнера ```redis-db``` запускаются после того, 
как тот стартанет, и после того, как он успешно пройдет ```healthcheck```.


Соберем и запустим контейнеры:
```shell
docker compose up --build
```

Теперь если мы отправим запрос на публикатор, 
чтобы тот отправил сообщение "message for channel bimba" в канал **bimba**, 
Два подписчика этого канала (**subscriber1** и **subscriber2**) получат сообщения:
```
subscriber1  | Received: message for channel bimba
subscriber2  | Received: message for channel bimba
```
Если же отправить сообщение в канал **bimba**, 
его поучит только **subscriber3**:
```
subscriber3  | Received: message for channel bumba
```
