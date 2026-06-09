# Мониторинг метрик сервера и БД через экспортеры

В этом уроке мы подключим сбор метрик через отдельные модули-экспортеры.
С их помощью в данном уроке будем собирать:
- основные метрики сервера (загруженности CPU, RAM, итд.) 
- основные метрики БД на примере postgres (время выполнение запросов, объемы буферов, количество подключений, итд.)

Также сделаем дашборды grafana для их просмотра и анализа.

Это нужно для того, чтобы на продакшене можно было в дальнейшем заблаговременно выявлять проблемы с производительностью, 
или же разбираться в произошедших нештатных ситуациях, анализировать поведение пользователей.

## Экспортеры

Поскольку prometheus сам по себе не может запускать какой-то код на сервере, 
метрики которого мы хотим мониторить 
(или например метрики той же БД), 
нам необхожимо сначала как-то их собрать с сервере в отдельном приложении.
Из этого приложения prometheus будет получать метрики по REST ручке 
(как и прошлом уроке мы получали метрики от бэкенда).
Такие приложения, которые собирают метрики и отдают их системе мониторинга, 
часто называют экпортерами.

### Экспортер метрик сервера (node_exporter)

Одной из самых частых задач является сбор метрик сервера 
(загруженность CPU, RAM, дисков, сети итд.).

Просто наблюдая за этими метриками мы сможем предотвратить много проблем в будущем 
(понимать когда необходимо развернуть пару дополнительных узлов для балансировки нагрузки, 
предотвратить переполнение дисков, 
предсказывать время, в которое нагрузка пользователей на сеть наибольшая).

В дальнейшем мы повесим на эти метрики алерты, 
чтобы система мониторинга автоматически оповещала нас о потенциальных проблемах. 

Добавим нод экспортер контейнер в наш **docker-compose.yml** конфиг:
```yaml
services:
  node-exporter:
    image: quay.io/prometheus/node-exporter:latest
    container_name: fastapi-l-36-node-exporter
    # network_mode: host
    # pid: host
    restart: unless-stopped
    ports:
      - "${NODE_EXPORTER_PORT-9100}:9100"
    volumes:
      - '/:/host:ro'
    command:
      - '--path.rootfs=/host'
    networks:
      - devup-lessons-fastapi-l-36
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9100/metrics"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```
Здесь чтобы node-exporter мог мониторить необходимые нам ресурсы:
- прокидываем вольюм для обработки данных о диске ```'/:/host:ro'```
- также в случае, если мы запускаем его на сервере, 
  мы можем указать ```network_mode: host``` и ```pid: host``` для того, 
  чтобы он мониторил ресурсы не окрежения сети докера, а хоста, на котором докер развернут
  (однако в данном уроке для простоты конфигов и использовать адреса node-exporter контейнера по внутреннему домену, 
  мы просто прокидываем сеть, в которой будут находиться и все остальные контейнеры этого урока)

Опишем prometheus и grafana в **docker-compose.yml**:
```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: fastapi-l-36-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=10d'
      - '--web.enable-lifecycle'
    networks:
      - devup-lessons-fastapi-l-36
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:9090/-/healthy"]
      interval: 40s
      timeout: 10s
      retries: 3
      start_period: 20s
#    extra_hosts:
#      - "host.docker.internal:host-gateway"  # for accessing server apps

  grafana:
    image: grafana/grafana
    container_name: fastapi-l-36-grafana
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_AUTH_ANONYMOUS_ENABLED=false
#      - GF_SERVER_ROOT_URL=/grafana  # for nginx reverse proxy
      - GF_PATHS_PROVISIONING=/etc/grafana/provisioning
      - TZ=${SYSTEM_TIMEZONE:-Europe/Moscow}
      - GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH=/etc/grafana/provisioning/dashboards/web-app-load-dashboard.json
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning/datasources:/etc/grafana/provisioning/datasources
      - ./grafana/provisioning/dashboards:/etc/grafana/provisioning/dashboards
    ports:
      - "3010:3000"
    networks:
      - devup-lessons-fastapi-l-36
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
```

В конфиг prometheus **prometheus/prometheus.yml** добавим node_exporter как источник метрик:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node_exporter'
    static_configs:
      - targets: ['fastapi-l-36-node-exporter:9100']
    scrape_interval: 5s  # вообще прям так часто собирать обычно не требуется, в данном примере это скорее для нашего удобства
    metrics_path: '/metrics'
```

Поскольку садача сбора метрик нагруженности сервера достаточно типовая, 
легче всего использовать уже существующий дашборд.
В этом примере взят достаточно подробный дашборд из https://grafana.com/grafana/dashboards, 
но ты всегда можешь найти себе какой-то, который считаешь более подходящим.

#### Бэк для моделирования нагрузки

Чтобы было чем моделировать нагрузку развернем простенький бэкенд.
По сути это тот же бэкенд. что и в прошлом уроке, 
только который еще и будет взаимодействовать с БД.

Код бэкенда можешь посмотреть в папке **api**.

Тогда контейнер для бэка будем описывать в **docker-compose.yml** следующим образом:
```yaml
services:
  api:
    build:
      context: api
    container_name: fastapi-l-36-api
    restart: unless-stopped
    environment:
      BASE_ROUTE_PATH: ${BASE_ROUTE_PATH}
      POSTGRES_SERVER: "fastapi-l-36-postgres"
      POSTGRES_PORT: 5432
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "8000:8000"
    networks:
      - devup-lessons-fastapi-l-36
    healthcheck:
      test: curl -f -s -S -o /dev/null http://localhost:8000/api/v1/app-info/versions || exit 1
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
```

Для того, чтобы в дальнейшем мониторить метрики БД, 
нам нужно будет влючить в postgres модуль pg_stats 
(как мы это делали в 9-м уроке про индексы в БД).

Контейнер БД с учетом активации модуля сбора статистики для postgres будет выглядеть тогда следующим образом:
```yaml
services:
  postgres:
    image: postgres:16
    container_name: fastapi-l-36-postgres
    restart: always
    command:
      - postgres
      - -c
      - shared_preload_libraries=${POSTGRES_SHARED_PRELOAD_LIBRARIES-pg_stat_statements}
      - -c
      - compute_query_id=${POSTGRES_COMPUTE_QUERY_ID-auto}
      - -c
      - pg_stat_statements.track=${PG_STAT_STATEMENTS_TRACK-all}
      - -c
      - pg_stat_statements.max=${PG_STAT_STATEMENTS_MAX-10000}
      - -c
      - pg_stat_statements.save=${PG_STAT_STATEMENTS_SAVE-on}
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres:/var/lib/postgresql
    ports:
      - "${POSTGRES_EXTERNAL_PORT-5435}:5432"
    networks:
      - devup-lessons-fastapi-l-36
    healthcheck:
      test: pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 10s
```

### Экспортер метрик БД (postgres_exporter)

Таже очень важно следить за состоянием БД, поэтому прикрутим экспортер и к ее метрикам.

Добавим в **docker-compose.yml**:
```yaml
  postgres-exporter:
    image: quay.io/prometheuscommunity/postgres-exporter:latest
    container_name: fastapi-l-36-postgres-exporter
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DATA_SOURCE_URI: "fastapi-l-36-postgres:5432/${POSTGRES_DB}?sslmode=disable"
      DATA_SOURCE_USER: ${POSTGRES_USER}
      DATA_SOURCE_PASS: ${POSTGRES_PASSWORD}
      PG_EXPORTER_EXTEND_QUERY_PATH: /etc/postgres_exporter/queries.yaml
    command:
      - '--collector.stat_statements'
      - '--collector.stat_statements.include_query'
    volumes:
      - ./postgres-exporter/queries.yaml:/etc/postgres_exporter/queries.yaml:ro
    ports:
      - "${POSTGRES_EXPORTER_PORT-9188}:9187"
    networks:
      - devup-lessons-fastapi-l-36
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:9187/metrics", "-o", "/dev/null"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
```

Добавим в конфиг prometheus **prometheus/prometheus.yml** и postgres-exporter как источник метрик:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node_exporter'
    static_configs:
      - targets: ['fastapi-l-36-node-exporter:9100']
    scrape_interval: 5s
    metrics_path: '/metrics'

  - job_name: 'postgres_exporter'
    static_configs:
      - targets: ['fastapi-l-36-postgres-exporter:9187']
    scrape_interval: 5s
    metrics_path: '/metrics'
```

Дашборд под postgres-exporter же тоже сделан на основе какого-то общедоступного.

При мониторинге БД важно смотреть за:
- сокростью выполнения запросов 
  (если конкретные запросы долгие по времени, 
  возможно на некоторые таблицы можно накинуть индексы или строить запросы на бэке иначе)
- количеством соединений (может быть если иих слишком много нужно обернуть подключения через pg_bouncer)
- количеством операций на чтение / запись (поможет в дальнейшем оптимизировать конфигурацию БД)
- объем закешироавнной постгресом информации (возможно порой придется чистить кеши)

#### Моделирование нагрузки

Теперь мы можем подергать эндпоинты бэка (при помощи того же Apache Benchmark) 
и посмотреть, что при большом количестве запросов к БД посмотреть будет отваливаться первым.
