# Обеспечивание отказоустойчивости Redis при помощи Redis Sentinel

Один сервер Redis не обеспечивает высокой доступности. 
Если сервер Redis выйдет из строя, 
все передаваемые через него сообщения или же кэш, будут потеряны, 
а приложение, использующее Redis, перестанет функционировать.

В высокодоступной архитектуре сообщения и данные должны быть реплицированы на несколько узлов, 
чтобы в случае сбоя одного из узлов система могла продолжить работу без потерь.

Для достижения высокой доступности используется кластеризация Redis (Redis Cluster) или Redis Sentinel:

- Redis Cluster — это распределённая система с шардированием данных, где каждый мастер-узел хранит определённую часть данных и имеет одну или несколько реплик. В случае сбоя мастер-узла одна из его реплик становится новым мастером. Это помогает обеспечить отказоустойчивость, так как данные распределяются между несколькими узлами.

- Redis Sentinel — это система управления фейловером, которая следит за состоянием узлов Redis и автоматически переключает роли между мастером и репликами в случае сбоя. Sentinel также уведомляет подключённые клиенты о том, что произошло переключение на новый мастер.

В данном уроке мы не будем разбирать кластеризацию с шардированием, 
а ограничемся примером работы с Redis Sentinel.
В конце этого урока мы получим систему, 
для которой не столь критичен отказ основного узла Redis, 
и которая способна в случае чего восстановить данные из реплик.

## Redis Sentinel

В данном уроке мы будем разбирать работу Redis Sentinel на примере приложений, общающихся через Pub/Sub.

Продюсеры подключаются к мастер-узлу, так как только мастер может принимать новые записи и публиковать сообщения в каналы Pub/Sub.

Консьюмеры также должны подключаться к мастер-узлу, поскольку только мастер транслирует сообщения по каналам Pub/Sub.

В случае, если мастер выходит из строя, Redis Sentinel выполняет фейловер и переводит одну из реплик в роль нового мастера. 
Продюсеры и консьюмеры должны переподключиться к новому мастеру для продолжения работы. 
Клиенты Redis можно настроить так, чтобы они автоматически находили новый мастер через Sentinel.

Redis Sentinel отслеживает состояние всех узлов Redis (мастера и реплик), 
регулярно отправляя запросы PING. 
Если мастер-узел перестает отвечать определенному количеству sentinel-узлов на запросы в течение определенного времени, 
Sentinel помечает его как недоступный и инициирует процесс фейловера. 
В рамках фейловера одна из реплик становится новым мастером, 
и клиенты перенаправляются на него. 
Это позволяет системе продолжать работу без существенных сбоев.

Стоит помнить, что при таком подходе:
- все подписки прирываются при переходе на новый мастер
- все сообщения, отправленные после отказа и до инициализации фейловера, будут потерямы
- такую систему на Redis Sentinel невозможно горизонтально масштабировать и шардировать данные между несколькими узлами 
  (для этого уже можно использовать Redis Cluster)
- при фейловере необходимо переключать подписчиков на новый мастер (поскольку они работают исключительно с мастером)

### Master и replica узлы Redis

Пусть конфиг master узла redis будет описан в **redis-master.conf** и выглядеть следующим образом:
```conf
port 6379
bind 0.0.0.0
protected-mode yes
requirepass master
dir /data
dbfilename dump.rdb
appendonly yes
```
Таким образом конфиг master узла не сильно отличается от обычного конфига redis.

Конфиг же replica узла redis будет описан в **redis-replica.conf** и выглядеть следующим образом:
```conf
port 6379
bind 0.0.0.0
protected-mode yes
requirepass master
dir /data
dbfilename dump.rdb
appendonly yes
replicaof redis-master 6379
```
Т.е. конфиг реплики аналогичный, только в нем указано, 
что это будет реплика от мастер узла (`replicaof redis-master 6379`).

Опишем создание одного master узла и двух реплик в **docker-compose.yml**:
```yaml
services:
  redis-master:
    image: redis:8.0-alpine
    container_name: redis-master
    hostname: redis-master
    ports:
      - "6389:6379"  # на случай, если у тебя на машине уже стоит redis, чтобы с ним не конфликтовать
    volumes:
      - ./redis-master.conf:/usr/local/etc/redis/redis.conf
    command: ["redis-server", "/usr/local/etc/redis/redis.conf"]
    networks:
      - redis-sentinel-net
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "$REDIS_PASSWORD", "-p", "6379", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

  redis-replica1:
    image: redis:8.0-alpine
    container_name: redis-replica1
    hostname: redis-replica1
    depends_on:
      redis-master:
        condition: service_healthy
    volumes:
      - ./redis-replica.conf:/usr/local/etc/redis/redis.conf
    command: ["redis-server", "/usr/local/etc/redis/redis.conf"]
    environment:
      REDIS_REPLICATION_MODE: "replica"
    networks:
      - redis-sentinel-net
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "$REDIS_PASSWORD", "-p", "6379", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

  redis-replica2:
    image: redis:8.0-alpine
    container_name: redis-replica2
    hostname: redis-replica2
    depends_on:
      redis-master:
        condition: service_healthy
    volumes:
      - ./redis-replica.conf:/usr/local/etc/redis/redis.conf
    command: ["redis-server", "/usr/local/etc/redis/redis.conf"]
    environment:
      REDIS_REPLICATION_MODE: "replica"
    networks:
      - redis-sentinel-net
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "$REDIS_PASSWORD", "-p", "6379", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

networks:
  redis-sentinel-net:
    driver: bridge
    name: redis-sentinel-net
```

### Sentinel узлы.

Теперь сделаем sentinel узлы, 
которые в случае совместного выявления отказа мастера будут переключать мастер на одну из реплик.

Пусть у нас будет следующая конфигурация sentinel узлов, указанная в **sentinel.conf**:
```conf
port 26379
bind 0.0.0.0
dir /tmp
protected-mode no

# Указываем, что Sentinel будет следить за мастером с именем "mymaster" на порту 6379
sentinel monitor mymaster 172.29.0.2 6379 2
# 2 - это количество Sentinel-ов, которые должны согласиться, что мастер недоступен
# 172.29.0.2 - адрес redis-master контейнера в redis-sentinel-net сети
# sentinel monitor mymaster redis-master 6379 2

# Время, через которое Sentinel будет считать мастер недоступным (в миллисекундах)
sentinel down-after-milliseconds mymaster 5000

# Время для фейловера (в миллисекундах)
sentinel failover-timeout mymaster 10000

# Как часто Sentinel будет проверять состояние реплик
sentinel parallel-syncs mymaster 1
```

Сделаем 3 копии sentinel при помощи указания `replicas: 3` в `deploy` параметре:
```yaml
  redis-sentinel:
    image: redis:8.0-alpine
    deploy:
      replicas: 3
    restart: always
    depends_on:
      redis-master:
        condition: service_healthy
    ports:
      - "26379-26381:26379"
    volumes:
      - ./sentinel.conf:/usr/local/etc/redis/sentinel.conf
    command: ["redis-server", "/usr/local/etc/redis/sentinel.conf", "--sentinel"]
    networks:
      - redis-sentinel-net
    healthcheck:
      test: ["CMD", "redis-cli", "-p", "26379", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
```
Здесь порты им выдаются из диапазона `26379-26381`:
```yaml
ports:
    - "26379-26381:26379"
```

Эта запись в **docker-compose.yml** будет эквивалентна следующей 
(т.е. мы использовали просто более компактную запись):
```yaml
  redis-sentinel1:
    image: redis:8.0-alpine
    container_name: redis-sentinel1
    hostname: redis-sentinel1
    restart: always
    depends_on:
      redis-master:
        condition: service_healthy
    ports:
      - "26379:26379"
    volumes:
      - ./sentinel.conf:/usr/local/etc/redis/sentinel.conf
    command: ["redis-server", "/usr/local/etc/redis/sentinel.conf", "--sentinel"]
    networks:
      - redis-sentinel-net
    healthcheck:
      test: ["CMD", "redis-cli", "-p", "26379", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

  redis-sentinel2:
    image: redis:8.0-alpine
    container_name: redis-sentinel2
    hostname: redis-sentinel2
    restart: always
    depends_on:
      redis-master:
        condition: service_healthy
    ports:
      - "26380:26379"
    volumes:
      - ./sentinel.conf:/usr/local/etc/redis/sentinel.conf
    command: ["redis-server", "/usr/local/etc/redis/sentinel.conf", "--sentinel"]
    networks:
      - redis-sentinel-net
    healthcheck:
      test: ["CMD", "redis-cli", "-p", "26379", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

  redis-sentinel3:
    image: redis:8.0-alpine
    container_name: redis-sentinel3
    hostname: redis-sentinel3
    restart: always
    depends_on:
      redis-master:
        condition: service_healthy
    ports:
      - "26381:26379"
    volumes:
      - ./sentinel.conf:/usr/local/etc/redis/sentinel.conf
    command: ["redis-server", "/usr/local/etc/redis/sentinel.conf", "--sentinel"]
    networks:
      - redis-sentinel-net
    healthcheck:
      test: ["CMD", "redis-cli", "-p", "26379", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
```

### Pub/Sub сервисы

Для данного примера мы просто возьмем сервисы из урока про Pub/Sub в Redis (l-28-redis-pub-sub).

Добавим в **docker-compose.yml** конейнер публикатора и контейнер подписчика:
```yaml
  publisher:
    build:
      context: api_publisher
    container_name: publisher
    environment:
      BASE_ROUTE_PATH: ${PUBLISHER_BASE_ROUTE_PATH-/api/v1}
      REDIS_SERVER: $REDIS_SERVER
      REDIS_PORT: $REDIS_PORT
      REDIS_DB: $REDIS_DB
      REDIS_USER: $REDIS_USER
      REDIS_PASSWORD: $REDIS_PASSWORD
    ports:
      - "${PUBLISHER_EXTERNAL_PORT-8000}:8000"
    networks:
      - redis-sentinel-net
    depends_on:
      redis-sentinel:
        condition: service_healthy

  subscriber:
    build:
      context: api_subscriber
    container_name: subscriber
    environment:
      CHANNEL_NAME: "bimba"
      REDIS_SERVER: $REDIS_SERVER
      REDIS_PORT: $REDIS_PORT
      REDIS_DB: $REDIS_DB
      REDIS_USER: $REDIS_USER
      REDIS_PASSWORD: $REDIS_PASSWORD
    networks:
      - redis-sentinel-net
    depends_on:
      redis-sentinel:
        condition: service_healthy
```

### Запуск

Добавим все необходимые переменные окружения в **.env**:
```
PUBLISHER_EXTERNAL_PORT = 8000
PUBLISHER_BASE_ROUTE_PATH="/api/v1"

# redis
REDIS_SERVER="redis-master"
REDIS_PORT="6379"
REDIS_DB="0"
REDIS_USER="default"
REDIS_PASSWORD="master"
```

Запустим все модули:
```shell
docker compose up -d --build
```

Попробуем отправить запросы с публикатора через swagger страничку http://localhost:8000/api/v1/docs. 
Отправить стоит в канал 'bimba', 
в таком случае мы сможем увидеть логах подписчика прочитанное сообщение при полмощи команды:
```shell
docker logs subscriber
```

## Переделывание публикатора и подписчика под работу с redis sentinel

<!-- TODO update l-28 for redis sentinel usage -->

Подробнее о redis sentinel ты можешь почитать здесь:
https://redis-doc-test.readthedocs.io/en/latest/topics/sentinel/.
