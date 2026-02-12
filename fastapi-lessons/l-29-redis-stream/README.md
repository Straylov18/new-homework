# Redis stream

Pub/Sub модель распространения сообщений, рассмотренная в прошлом уроке, 
конечно была очень проста и удобна, однако имеет ряд недостатков:
- если издатель по каким-либо причинам выходит из строя, 
то он теряет всех своих подписчиков
- издатель может перегрузить работой своих подписчиков, 
если данные публикуются быстрее, чем обрабатываются
- сообщение удаляется из буфера издателя сразу после публикации, не зависимо от того, 
какому числу подписчиков оно доставлено и как быстро те сумели обработать это сообщение

Также порой мы может быть не хотим, чтобы все сообщения обрабатывались одновременно.
Или же порой мы хотим удостовериться, 
что сообщение получил и успешно обработал хотя бы один подписчик.

В этом случае нам удобнее будет использовать механизм стриминга (redis stream).

## Producer

Для начала сделаем сервис, который будет наполнять потоки сообщениями в папке **api_producer**.

Конфиг у него пусть будет такой же, как и в прошлом уроке 
(параметры для подключения к редису и префикс для ручек).

Добавим ручку для добавления n сообщений в указанный стрим ```/produce/{channel}``` 
в **api_producer/src/main.py**:
```python
import json
from time import time

import uvicorn
from fastapi import Depends, FastAPI

from src.adapter.redis import get_redis_connection
from src.config import settings

app = FastAPI(
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs",
)


@app.get('/produce/{channel}')
async def publish_message(stream_key: str, message: str, messages_number: int = 1,
                          redis_session=Depends(get_redis_connection)) -> str:
    for i in range(messages_number):
        data = {
            'time': time(),
            'message': message,
            'number': i,
            'balbla': 'blablabla'
        }
        msg_id = await redis_session.xadd(
            stream_key,
            {'ts': time(), 'v': i, 'data': json.dumps(data)}
        )
        print(f'Producer sent {msg_id}')
    success_message = f'stream {stream_key} length: {redis_session.xlen(stream_key)}'
    print(success_message)
    return success_message


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
```
Здесь функция ```redis_session.xadd(...)``` 
первым параметром принимает название стрима в редисе, 
а вторым параметром данные в виде словаря, 
которые будут разбиты по соответствующим колонкам внутри стрима редиса.

В отличие от Pub/Sub, streams не читаются получателями сразу.
Сообщения в стримах копятся, 
а получатели лишь вытягивают их.
Поэтому можно быть уверенным, 
что сообщение не потеряется в случае разрыва соединения. 
Получатели же будут брать сообщения и отмечать их как прочитанные, 
чтобы не взять одно и то же сообщение несколько раз.

Добавим также ручку для удаления всех сообщений из потока сообщений по ключу:
```python
@app.delete('/delete-messages/{stream_key}')
async def delete_messages(stream_key: str, redis_session=Depends(get_redis_connection)):
    s1 = await redis_session.xread(streams={stream_key: 0})
    for streams in s1:
        stream_name, messages = streams
        # удаляем все id из листа сообщений стрима
        for i in messages:
            await redis_session.xdel(stream_name, i[0])
```
Эта ручка будет удалять сообщения из очереди редиса, 
поэтому удаляться будут как обработанные, так и не обработанные сообщения.

## Consumer

Теперь пропишем сервис потребителей сообщений.

Можно конечно получать сообщения напрямую, 
но зачастую получателей объединяют в группы, 
чтобы нагрузка равномерно распределялась между членами группы.
В таком случае только один потребитель из группы будет обрабатывать сообщение.
При этом если будет несколько разных групп потребителей, 
сообщение обработается по разу в каждой группе.

При старте мы будем задавать потребителя ключ стрима, 
к которому ему нужно подключаться, 
название группы получателей и название самого потребителя.

Тогда **api_consumer/src/config.py** будет выглядеть следующим образом:
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

    REDIS_CACHE_EXPIRE_TIME: int = 10

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
    STREAM_KEY: str = 'Timon'
    GROUP_NAME: str = 'gn1'
    CONSUMER_NAME: str = 'cn1'
    REDIS: RedisSettings = RedisSettings()


settings = Settings()
```

Теперь напишем метод для обработки сообщений из стрима в **api_consumer/src/main.py**:
```python
import asyncio
import json

from redis.exceptions import ResponseError

from adapter.redis import get_redis_connection
from config import settings


async def consume_messages():
    redis_session = await get_redis_connection()

    # Create consumer group
    try:
        await redis_session.xgroup_create(
            settings.STREAM_KEY,
            settings.GROUP_NAME, '$',
            mkstream=True
        )
    except ResponseError as e:
        print(f'raised: {e}')  # Already exists

    print('Consumer waiting for messages...')

    while True:
        messages = await redis_session.xreadgroup(
            settings.GROUP_NAME,
            settings.CONSUMER_NAME,
            streams={settings.STREAM_KEY: '>'},
            count=1,
            block=1000
        )

        if not messages:
            continue

        for stream, msg_list in messages:
            for msg_id, fields in msg_list:
                data = json.loads(fields['data'])
                print(f'Consumer received: {msg_id} -> {data}')
                await redis_session.xack(settings.STREAM_KEY, settings.GROUP_NAME, msg_id)

    await redis_session.close()


if __name__ == '__main__':
    asyncio.run(consume_messages())
```
Здесь:
- сначала в redis каждый раз создается группа потребителей (если уже есть, то ничего страшного)
    ```python
    await redis_session.xgroup_create(
            settings.STREAM_KEY,
            settings.GROUP_NAME, '$',
            mkstream=True
        )
    ```
- потом до бесконечности из редиса пачками вычитываются сообщения 
для данной группы, которые еще не обработаны
    ```python
    messages = await redis_session.xreadgroup(
        settings.GROUP_NAME,
        settings.CONSUMER_NAME,
        streams={settings.STREAM_KEY: '>'},
        count=1,
        block=1000
    )
    ```
- потом обрабатываются все сообщения 
    ```python
    for stream, msg_list in messages:
        for msg_id, fields in msg_list:
            data = json.loads(fields['data'])
            print(f'Consumer received: {msg_id} -> {data}')
            await redis_session.xack(settings.STREAM_KEY, settings.GROUP_NAME, msg_id)
    ```
    и помечаются как прочитанные для этой группы потребителей 
    (```redis_session.xack(settings.STREAM_KEY, settings.GROUP_NAME, msg_id)```)

## Развертка примера

Проверим что все работает как надо, 
запустив наше приложение с разными группами потребителей разных стримов 
через **docker-compose.yml**.

Сам **docker-compose.yml** пусть будет следующим:
```yml
---
services:

  producer:
    build:
      context: api_producer
    container_name: producer
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
      - redis-stream
    depends_on:
      redis-db-streams:
        condition: service_healthy

  consumer1-t-gn1:
    build:
      context: api_consumer
    container_name: consumer1-t-gn1
    environment:
      STREAM_KEY: "Timon"
      GROUP_NAME: "gn1"
      CONSUMER_NAME: "cn1"
      REDIS_SERVER: $REDIS_SERVER
      REDIS_PORT: $REDIS_PORT
      REDIS_DB: $REDIS_DB
      REDIS_USER: $REDIS_USER
      REDIS_PASSWORD: $REDIS_PASSWORD
    networks:
      - redis-stream
    depends_on:
      redis-db-streams:
        condition: service_healthy

  consumer2-t-gn1:
    build:
      context: api_consumer
    container_name: consumer2-t-gn1
    environment:
      STREAM_KEY: "Timon"
      GROUP_NAME: "gn1"
      CONSUMER_NAME: "cn2"
      REDIS_SERVER: $REDIS_SERVER
      REDIS_PORT: $REDIS_PORT
      REDIS_DB: $REDIS_DB
      REDIS_USER: $REDIS_USER
      REDIS_PASSWORD: $REDIS_PASSWORD
    networks:
      - redis-stream
    depends_on:
      redis-db-streams:
        condition: service_healthy

  consumer3-t-gn2:
    build:
      context: api_consumer
    container_name: consumer3-t-gn2
    environment:
      STREAM_KEY: "Timon"
      GROUP_NAME: "gn2"
      CONSUMER_NAME: "cn3"
      REDIS_SERVER: $REDIS_SERVER
      REDIS_PORT: $REDIS_PORT
      REDIS_DB: $REDIS_DB
      REDIS_USER: $REDIS_USER
      REDIS_PASSWORD: $REDIS_PASSWORD
    networks:
      - redis-stream
    depends_on:
      redis-db-streams:
        condition: service_healthy

  consumer4-p-gn1:
    build:
      context: api_consumer
    container_name: consumer4-p-gn1
    environment:
      STREAM_KEY: "Pumbaa"
      GROUP_NAME: "gn1"
      CONSUMER_NAME: "cn4"
      REDIS_SERVER: $REDIS_SERVER
      REDIS_PORT: $REDIS_PORT
      REDIS_DB: $REDIS_DB
      REDIS_USER: $REDIS_USER
      REDIS_PASSWORD: $REDIS_PASSWORD
    networks:
      - redis-stream
    depends_on:
      redis-db-streams:
        condition: service_healthy

  redis-db-streams:
    image: "redis:8"
    container_name: redis-db-streams
    environment:
      REDIS_USER_PASSWORD: $REDIS_PASSWORD
    networks:
      - redis-stream
    ports:
      - "${REDIS_EXTERNAL_PORT-6380}:6379"
    healthcheck:
      test: [ "CMD", "redis-cli", "-a", "$REDIS_PASSWORD", "ping" ]
      interval: 2s
      timeout: 5s
      retries: 5
    restart: unless-stopped

networks:
  redis-stream:
```
Здесь есть:
- один ```producer``` контейнер,
  с которого мы будем отправлять сообщения
- 4 контейнера потребителей
  3 подписаны на канал 'Timon':
    - ```subscriber1-t-gn1``` (сидит в группе **gn1**)
    - ```subscriber2-t-gn1``` (подписан на канал **gn1**)
    - ```subscriber3-t-gn2``` (подписан на канал **gn2**)
  1 на канал Pumbaa
    - ```consumer4-p-gn1``` (подписан на канал **gn1**)
- контейнер с редисом ```redis-db-stream```

Запустим это все с помощью:
```shell
docker compose up --build
```

Посмотрим как 4-й потребитель будет один обрабатывать сообщения из 'Pumbaa' потока.
При отправке запроса ```http://localhost:8000/produce/Pumbaa/5?message=awim%20bavey``` мы получим следующие логи:
```
producer          | Producer sent 1770890489312-0
producer          | Producer sent 1770890489312-1
producer          | Producer sent 1770890489312-2
producer          | Producer sent 1770890489312-3
producer          | Producer sent 1770890489313-0
consumer4-p-gn1   | Consumer received: 1770890489312-0 -> {'time': 1770890487.076165, 'message': 'awim bavey', 'number': 0, 'balbla': 'blablabla'}
consumer4-p-gn1   | Consumer received: 1770890489312-1 -> {'time': 1770890487.0761764, 'message': 'awim bavey', 'number': 1, 'balbla': 'blablabla'}
consumer4-p-gn1   | Consumer received: 1770890489312-2 -> {'time': 1770890487.0761983, 'message': 'awim bavey', 'number': 2, 'balbla': 'blablabla'}
consumer4-p-gn1   | Consumer received: 1770890489312-3 -> {'time': 1770890487.0762095, 'message': 'awim bavey', 'number': 3, 'balbla': 'blablabla'}
consumer4-p-gn1   | Consumer received: 1770890489313-0 -> {'time': 1770890487.076221, 'message': 'awim bavey', 'number': 4, 'balbla': 'blablabla'}
```
Id сообщения будет в виде '{время}-{номер_сообщения_в_это_время}'.
Как можно увидеть наш потребитель обрабатывал последовательно все пять сообщений, 
пока они не кончились. 

Теперь закинем 4 сообщения в стрим 'Timon' через запрос к 
```http://localhost:8000/produce/Timon/4?message=hakuna%20matata```:
```
producer          | Producer sent 1770891758867-0
consumer2-t-gn1   | Consumer received: 1770891758867-0 -> {'time': 1770891758.84774, 'message': 'hakuna matata', 'number': 0, 'balbla': 'blablabla'}
consumer3-t-gn2   | Consumer received: 1770891758867-0 -> {'time': 1770891758.84774, 'message': 'hakuna matata', 'number': 0, 'balbla': 'blablabla'}
producer          | Producer sent 1770891758868-0
consumer1-t-gn1   | Consumer received: 1770891758868-0 -> {'time': 1770891758.868111, 'message': 'hakuna matata', 'number': 1, 'balbla': 'blablabla'}
producer          | Producer sent 1770891758869-0
consumer3-t-gn2   | Consumer received: 1770891758868-0 -> {'time': 1770891758.868111, 'message': 'hakuna matata', 'number': 1, 'balbla': 'blablabla'}
consumer2-t-gn1   | Consumer received: 1770891758869-0 -> {'time': 1770891758.8689113, 'message': 'hakuna matata', 'number': 2, 'balbla': 'blablabla'}
producer          | Producer sent 1770891758869-1
consumer1-t-gn1   | Consumer received: 1770891758869-1 -> {'time': 1770891758.8696053, 'message': 'hakuna matata', 'number': 3, 'balbla': 'blablabla'}
consumer3-t-gn2   | Consumer received: 1770891758869-0 -> {'time': 1770891758.8689113, 'message': 'hakuna matata', 'number': 2, 'balbla': 'blablabla'}
consumer3-t-gn2   | Consumer received: 1770891758869-1 -> {'time': 1770891758.8696053, 'message': 'hakuna matata', 'number': 3, 'balbla': 'blablabla'}
```
Здесь мы видим, что в первой группе сообщения 
равномерно распределялись между двумя потребителями:
```
consumer2-t-gn1   | Consumer received: 1770891758867-0 -> {'time': 1770891758.84774, 'message': 'hakuna matata', 'number': 0, 'balbla': 'blablabla'}
consumer1-t-gn1   | Consumer received: 1770891758868-0 -> {'time': 1770891758.868111, 'message': 'hakuna matata', 'number': 1, 'balbla': 'blablabla'}
consumer2-t-gn1   | Consumer received: 1770891758869-0 -> {'time': 1770891758.8689113, 'message': 'hakuna matata', 'number': 2, 'balbla': 'blablabla'}
consumer1-t-gn1   | Consumer received: 1770891758869-1 -> {'time': 1770891758.8696053, 'message': 'hakuna matata', 'number': 3, 'balbla': 'blablabla'}
```
Также видно, что сообщения приходили и на потребителя из 2-й группы:
```
consumer3-t-gn2   | Consumer received: 1770891758867-0 -> {'time': 1770891758.84774, 'message': 'hakuna matata', 'number': 0, 'balbla': 'blablabla'}
consumer3-t-gn2   | Consumer received: 1770891758868-0 -> {'time': 1770891758.868111, 'message': 'hakuna matata', 'number': 1, 'balbla': 'blablabla'}
consumer3-t-gn2   | Consumer received: 1770891758869-0 -> {'time': 1770891758.8689113, 'message': 'hakuna matata', 'number': 2, 'balbla': 'blablabla'}
consumer3-t-gn2   | Consumer received: 1770891758869-1 -> {'time': 1770891758.8696053, 'message': 'hakuna matata', 'number': 3, 'balbla': 'blablabla'}
```

Таким образом количеством групп можно контролировать 
сколько раз будут обрабатываться сообщения 
(зачастую у разных групп разная логика обработки).
В рамках одной группы же можно распределять нагрузку 
при помощи добавления новых потребителей.
