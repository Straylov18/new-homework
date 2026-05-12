# Мониторинг метрик бэкенд приложения

В этом уроке мы подключим сбор метрик бэекенд приложения и отобразим их в виде удобных и понятных графиков. 

Это нужно для того, чтобы на продакшене лучше отслеживать состояние приложения, 
заблаговременно выявлять проблемы с производительностью, 
разбираться в произошедших нештатных ситуациях, анализировать поведение пользователей.

## Пакетный менеджер uv

В этом уроке мы вместо **poetry** будем использовать пакетный менеджер **uv**.

Это более современный пакетный менеджер, чем **poetry**. 
Он немного быстрее, плюс с его помощью удобнее использовать для проекта нужную версию python 
(если указанной версии python нет локально, **uv** сам скачает ее).

Чтобы создать конфигурацию проекта через **uv** можно воспользоваться командой:
```shell
uv init
```
В этот момент он создаст файл **.python-version**, 
в котором будет указана версия python для этого проекта (которую в случае чего можно относительно легко поменять).

Чтобы зафиксировать зависимости, создав **uv.lock**:
```shell
uv lock
```

Чтобы добавить зависимости:
```shell
uv add fastapi
# чтобы добавить в какую-то группу зависимостей, например в 'test'
uv add --group test flake8
```

Чтобы синхронизовать зависимости:
```shell
uv sync
# чтобы сделать это для группы зависимостей 'test'
uv sync --group test
```

## Сбор метрик через prometheus

**Prometheus** - это система мониторинга и оповещения с открытым исходным кодом, 
которая собирает, хранит и анализирует метрики работы 
приложений, серверов и инфраструктуры в реальном времени с заданной периодичностью.

Для сбора метрик **prometheus** использует pull модель сбора метрик, 
т.е. он с заданным интервалом дергает источники метрик через http запросы.

Собранные данные сохраняются в специализированной временной базе данных (**TSDB**) в формате временных рядов.
**TSDB** - это специализированная база данных, 
где метрики хранятся в виде пар ключ (временная метка, значение в указанный момент времени).

Принцип работы **prometheus**:
- опрос источников метрик с заданной периодичностью 
  (может опрашиваться как специализированная ручка бэкенда, 
  так и готовый exporter модуль как те же node_exporter, postgres_exporter итд.)
- запись метрик в **TSDB**
- выдача метрик через http запросы
- также есть возможность отправлять сообщения об около-критических или критических ситуациях

### Какие есть популярные альтернативы?

Стоит упомянуть, что **prometheus** не единственное решение.
Одной из популярных альтернатив является **zabbix**

**Zabbix** содержит в себе сразу все необходимое для старта, в отличие от **prometheus**, 
который является более модульным решением. 
Т.е. в **zabbix** много чего есть из коробки, 
но **prometheus** легче будет потом масштабировать.

Также **zabbix** хранит данные в SQL базах данных, 
что позволяет удобно хранить их долгое время, 
однако при большом объем данных могут возникнуть проблемы 
(но в **prometheus** можно тоже подключить модуль длительного хранения метрик). 
Ну и PromQL для вытягивания метрик из **prometheus** на самом деле часто удобнее для обработки метрик.

Также **zabbix** поддерживает большее количество протоколов сбора логов и работает на push системе 
(те метрики закидываются в него, а не он их тянет из мониторящихся систем).

## Выдача метрик о запросах бэкенд приложения

Чтобы потренироваться в выдаче метрик, 
для начала напишем небольшое бэкенд приложение, в котором будет:
- возможность логина
- ручкой выдачи версии приложения, на которую повесим healthcheck для docker контейнера бэка
- пару типов ручек с параметризацией в пути (**/joke/{id}**, **/meme/{id}**)
- **middleware** слоем, в котором будут собираться все метрики
- ручкой для выдачи метрик **prometheus** узлу

### Слой метрик

Добавим в приложение еще один слой, которого не было раньше - слой метрик (**metrics**).
В нем мы будем описывать и хранить все метрики, которые будем собирать с бэкенда.

#### Хранение информации о метриках

Чтобы приложение могло выдавать метрики по http ручке в любой момент времени, 
оно должно хранить их в какой-то сущности.

Для хранения и парсинга метрик в удобный вид легче всего будет воспользоваться функционалом специальной библиотеки, 
специализированной под общение с **prometheus**. Установим ее в проект:
```shell
uv add prometheus-client
```

В ней для хранения метрик есть специальный класс `CollectorRegistry`, 
объект которого мы будем указывать во всех метриках, чтобы они складывали свои значения именно в него.

Для хранения `CollectorRegistry` напишем контейнер с фабрикой в **src/metrics/container/collector_container.py**: 
```python
from prometheus_client import CollectorRegistry


class RegistryContainer():
    _registry = None

    @classmethod
    def registry(cls) -> CollectorRegistry:
        if cls._registry is None:
            cls._registry = CollectorRegistry()
        return cls._registry
```

#### Описание базовых метрик http запросов

Для начала опишем самые часто используемые метрики для анализа http запросов: 
```python
from prometheus_client import Counter, Histogram

from src.metrics.container.collector_container import RegistryContainer

# Counter: increasing value (total number of calls)
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code'],
    registry=RegistryContainer.registry()
)

# Histogram: distributing values (execution time)
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    registry=RegistryContainer.registry()
)

# Counting API calls
api_calls_total = Counter(
    'api_calls_total',
    'Total number of API calls by type',
    ['api_type'],
    registry=RegistryContainer.registry()
)

# Separate counters for errors
http_errors_4xx_total = Counter(
    'http_errors_4xx_total',
    'Total number of 4xx HTTP errors',
    ['endpoint', 'status_code'],
    registry=RegistryContainer.registry()
)

http_errors_5xx_total = Counter(
    'http_errors_5xx_total',
    'Total number of 5xx HTTP errors',
    ['endpoint', 'status_code'],
    registry=RegistryContainer.registry()
)
```
Здесь в качестве метрик собираются:
- `http_requests_total` - общее количество запросов разных типов
- `http_request_duration_seconds` - время жизни запросов разных типов
- `api_calls_total` - общее количество запросов при обращении к разным видам сущностей
- `http_errors_4xx_total` - общее количество четырехсотых ошибок (отловленных бэкендом)
- `http_errors_5xx_total` - общее количество пятисотых ошибок (которые бэкенд не ожидал)

Рассмотрим поподробнее одну из метрик:
```python
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code'],
    registry=RegistryContainer.registry()
)
```
Здесь:
- `'http_requests_total'` - задаем название метрики
- `'Total number of HTTP requests'` - задаем описание метрики
- `['method', 'endpoint', 'status_code']` - задаем метки (labels), 
  по которым в рамках этой метрики данные будут классифицироваться в дальнейшем
  (будет писаться сразу несколько кучек под разные наборы разных меток)
- `registry=RegistryContainer.registry()` - указываем в каком registry их хранить

В файле **middleware.py** напишем middleware класс, 
который будет обрабатывать все эти метрики перед каждым запросом:
```python
import time
from typing import Awaitable, Callable

from fastapi import FastAPI, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from src.metrics.http_requests import (api_calls_total, http_errors_4xx_total,
                                       http_errors_5xx_total,
                                       http_request_duration_seconds,
                                       http_requests_total)


class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # executing request
        start_time = time.time()
        try:
            response = await call_next(request)
        except Exception as e:
            response = Response(
                content=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                media_type="text/plain"
            )
        duration = time.time() - start_time

        path = request.url.path
        # normalize paths: /api/v1/activities/12345 -> /api/v1/activities/{uid}
        if path.startswith('/api/v1/'):
            parts = path.split('/')
            if len(parts) > 4 and parts[4].isdigit():
                parts[4] = '{uid}'
                path = '/'.join(parts)

        # collecting metrics
        http_requests_total.labels(
            method=request.method,
            endpoint=path,
            status_code=str(response.status_code)
        ).inc()

        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=path
        ).observe(duration)

        # tracking API calls
        if path.startswith('/api/v1/'):
            if len(path.split('/')) > 3:
                api_type = path.split('/')[3]
            else:
                api_type = 'unknown'
            api_calls_total.labels(api_type=api_type).inc()

        # separate errors counting
        status_code = response.status_code
        if 400 <= status_code < 500:
            http_errors_4xx_total.labels(endpoint=path, status_code=str(status_code)).inc()
        elif status_code >= 500:
            http_errors_5xx_total.labels(endpoint=path, status_code=str(status_code)).inc()

        return response
```
Здесь в `dispatch` методе мы (подряд по блокам кода):
- рассчитываем время запроса и в случае необработанной ошибки корректно обрабатываем ее как 500-ю, 
  чтоб код ниже этого блока не пропускался
- нормализуем пути 
  (чтобы в метрики пути с разными id для одинаковых сущностей не писались с разными метками)
- накручиваем `http_requests_total` метрику,
  ранжируя ее по необходимым меткам 
  (конкретно тут по типу запроса, пути запроса и по коду ответа)
- накапливаем статистику в метрике `http_request_duration_seconds` 
  (опять же разбивая на группы с учетом меток)
- накручиваем `api_calls_total` метрику, 
  учитывая лишь первую часть префикса пути, 
  которая в данном приложении отвечает за тип сущности (с которой взаимодействуем)
- накручиваем `http_errors_4xx_total` и `http_errors_5xx_total` метрики

В **src/main.py** теперь нужно подключить получившийся middleware класс:
```python
app.add_middleware(MetricsMiddleware)
```

#### Метрики бизнес логики

Также опишем метрики для анализа поведения пользователей (бизнес метрики):
```python
from prometheus_client import Counter

from src.metrics.container.collector_container import RegistryContainer

# --- Auth ---

user_logins_total = Counter(
    'user_logins_total',
    'Total number of user logins',
    registry=RegistryContainer.registry()
)

user_logins_succeed_total = Counter(
    'user_logins_succeed_total',
    'Total number of successful user logins',
    registry=RegistryContainer.registry()
)
```
Здесь в качестве метрик собираются:
- `user_logins_total` - общее количество попыток входа в систему
- `user_logins_succeed_total` - общее количество успешных входов в систему

в зависимости от приложения так-то можно собирать какие угодно метрики бизнес логики.

#### Расчет метрик при обработке ручек

Пусть **src/route/joke.py** будет ручка для выдачи шутки по ее id:
```python
from fastapi.routing import APIRouter

router = APIRouter(prefix="/joke")

jokes = ['joke 1', 'joke 2', 'joke 3']

@router.get('/{id}',
            response_model=str)
async def get_joke(id: int) -> str:
    return jokes[id]
```

А в **src/route/meme.py** будет ручка для выдачи мэма по его id:
```python
from fastapi.routing import APIRouter

router = APIRouter(prefix="/memes")

memes = ['meme 1', 'meme 2', 'meme 3']

@router.get('/{id}',
            response_model=str)
async def get_meme(id: int) -> str:
    return memes[id]
```

Для ручки логина же будем собирать метрики при инициации запроса и в случае успешной его обработки.
Опишем ручку логина в **src/route/user.py**:
```python
from fastapi import Response
from fastapi.routing import APIRouter

from src.config import settings
from src.exception.common import ForbiddenException
from src.metrics.business_logic import (user_logins_succeed_total,
                                        user_logins_total)
from src.schema.user import UserLogin
from src.utils.auth import create_access_token

router = APIRouter(prefix="/user")


@router.post('/login',
             response_model=str,
             responses={
                 403: {"description": "Incorrect login or password"}
             })
async def login(body: UserLogin, response: Response) -> str:
    # инкрементируем колическво логинов в систему
    user_logins_total.inc()

    if body.login != settings.ADMIN_LOGIN or body.password != settings.ADMIN_PASSWORD:
        raise ForbiddenException(reason="Incorrect login or password", action="login")
    jwt_token_data = {
        "user_login": str(settings.ADMIN_LOGIN),
    }
    jwt_token = create_access_token(jwt_token_data)
    response.set_cookie("access_token", jwt_token)

    # инкрементируем колическво успешных логинов в систему
    user_logins_succeed_total.inc()

    return "Login succeeded"


@router.post("/logout")
async def logout(response: Response) -> str:
    response.delete_cookie(key="access_token")
    return "Logout succeeded"
```

И теперь опишем собственно ручку для получения всех текущих метрик бэкенд приложения:
```python
from fastapi.responses import PlainTextResponse
from fastapi.routing import APIRouter
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from src.metrics.container.collector_container import RegistryContainer

router = APIRouter(prefix="/app-info")


@router.get("/metrics")
async def metrics() -> PlainTextResponse:
    """Prometheus metrics endpoint"""
    return PlainTextResponse(
        generate_latest(RegistryContainer.registry()),
        media_type=CONTENT_TYPE_LATEST
    )
```
Здесь `PlainTextResponse` переведет текущие метрики нашего registry
(`generate_latest(RegistryContainer.registry())`) 
в формат понятный для prometheus.

Формат этот будет выглядеть примерно так:
```
# HELP http_requests_total Total number of HTTP requests
# TYPE http_requests_total counter
http_requests_total{endpoint="/api/v1/app-info/versions",method="GET",status_code="200"} 21.0
http_requests_total{endpoint="/api/v1/app-info/metrics",method="GET",status_code="200"} 44.0
http_requests_total{endpoint="/api/v1/docs",method="GET",status_code="200"} 1.0
http_requests_total{endpoint="/api/v1/openapi.json",method="GET",status_code="200"} 1.0
http_requests_total{endpoint="/api/v1/meme/{uid}",method="GET",status_code="404"} 8000.0
http_requests_total{endpoint="/api/v1/joke/{uid}",method="GET",status_code="200"} 6000.0
http_requests_total{endpoint="/api/v1/joke/{uid}",method="GET",status_code="500"} 2000.0
http_requests_total{endpoint="/api/v1/user/login",method="GET",status_code="405"} 2000.0
# HELP http_requests_created Total number of HTTP requests
# TYPE http_requests_created gauge
http_requests_created{endpoint="/api/v1/app-info/versions",method="GET",status_code="200"} 1.7785485936905015e+09
http_requests_created{endpoint="/api/v1/app-info/metrics",method="GET",status_code="200"} 1.7785485943666394e+09
http_requests_created{endpoint="/api/v1/docs",method="GET",status_code="200"} 1.7785485967953575e+09
http_requests_created{endpoint="/api/v1/openapi.json",method="GET",status_code="200"} 1.7785485980294118e+09
http_requests_created{endpoint="/api/v1/meme/{uid}",method="GET",status_code="404"} 1.778548680642148e+09
http_requests_created{endpoint="/api/v1/joke/{uid}",method="GET",status_code="200"} 1.7785486945187416e+09
http_requests_created{endpoint="/api/v1/joke/{uid}",method="GET",status_code="500"} 1.778548706303784e+09
http_requests_created{endpoint="/api/v1/user/login",method="GET",status_code="405"} 1.7785487098675182e+09
# HELP http_request_duration_seconds HTTP request duration in seconds
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/versions",le="0.005",method="GET"} 19.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/versions",le="0.01",method="GET"} 21.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/versions",le="0.025",method="GET"} 21.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/versions",le="0.05",method="GET"} 21.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/versions",le="0.075",method="GET"} 21.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/versions",le="0.1",method="GET"} 21.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/versions",le="0.25",method="GET"} 21.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/versions",le="0.5",method="GET"} 21.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/versions",le="0.75",method="GET"} 21.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/versions",le="1.0",method="GET"} 21.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/versions",le="2.5",method="GET"} 21.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/versions",le="5.0",method="GET"} 21.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/versions",le="7.5",method="GET"} 21.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/versions",le="10.0",method="GET"} 21.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/versions",le="+Inf",method="GET"} 21.0
http_request_duration_seconds_count{endpoint="/api/v1/app-info/versions",method="GET"} 21.0
http_request_duration_seconds_sum{endpoint="/api/v1/app-info/versions",method="GET"} 0.0256807804107666
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/metrics",le="0.005",method="GET"} 32.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/metrics",le="0.01",method="GET"} 44.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/metrics",le="0.025",method="GET"} 44.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/metrics",le="0.05",method="GET"} 44.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/metrics",le="0.075",method="GET"} 44.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/metrics",le="0.1",method="GET"} 44.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/metrics",le="0.25",method="GET"} 44.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/metrics",le="0.5",method="GET"} 44.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/metrics",le="0.75",method="GET"} 44.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/metrics",le="1.0",method="GET"} 44.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/metrics",le="2.5",method="GET"} 44.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/metrics",le="5.0",method="GET"} 44.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/metrics",le="7.5",method="GET"} 44.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/metrics",le="10.0",method="GET"} 44.0
http_request_duration_seconds_bucket{endpoint="/api/v1/app-info/metrics",le="+Inf",method="GET"} 44.0
http_request_duration_seconds_count{endpoint="/api/v1/app-info/metrics",method="GET"} 44.0
http_request_duration_seconds_sum{endpoint="/api/v1/app-info/metrics",method="GET"} 0.19114351272583008
http_request_duration_seconds_bucket{endpoint="/api/v1/docs",le="0.005",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/docs",le="0.01",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/docs",le="0.025",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/docs",le="0.05",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/docs",le="0.075",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/docs",le="0.1",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/docs",le="0.25",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/docs",le="0.5",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/docs",le="0.75",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/docs",le="1.0",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/docs",le="2.5",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/docs",le="5.0",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/docs",le="7.5",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/docs",le="10.0",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/docs",le="+Inf",method="GET"} 1.0
http_request_duration_seconds_count{endpoint="/api/v1/docs",method="GET"} 1.0
http_request_duration_seconds_sum{endpoint="/api/v1/docs",method="GET"} 0.0004894733428955078
http_request_duration_seconds_bucket{endpoint="/api/v1/openapi.json",le="0.005",method="GET"} 0.0
http_request_duration_seconds_bucket{endpoint="/api/v1/openapi.json",le="0.01",method="GET"} 0.0
http_request_duration_seconds_bucket{endpoint="/api/v1/openapi.json",le="0.025",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/openapi.json",le="0.05",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/openapi.json",le="0.075",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/openapi.json",le="0.1",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/openapi.json",le="0.25",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/openapi.json",le="0.5",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/openapi.json",le="0.75",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/openapi.json",le="1.0",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/openapi.json",le="2.5",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/openapi.json",le="5.0",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/openapi.json",le="7.5",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/openapi.json",le="10.0",method="GET"} 1.0
http_request_duration_seconds_bucket{endpoint="/api/v1/openapi.json",le="+Inf",method="GET"} 1.0
http_request_duration_seconds_count{endpoint="/api/v1/openapi.json",method="GET"} 1.0
http_request_duration_seconds_sum{endpoint="/api/v1/openapi.json",method="GET"} 0.011320114135742188
http_request_duration_seconds_bucket{endpoint="/api/v1/meme/{uid}",le="0.005",method="GET"} 4180.0
http_request_duration_seconds_bucket{endpoint="/api/v1/meme/{uid}",le="0.01",method="GET"} 7969.0
http_request_duration_seconds_bucket{endpoint="/api/v1/meme/{uid}",le="0.025",method="GET"} 7971.0
http_request_duration_seconds_bucket{endpoint="/api/v1/meme/{uid}",le="0.05",method="GET"} 8000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/meme/{uid}",le="0.075",method="GET"} 8000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/meme/{uid}",le="0.1",method="GET"} 8000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/meme/{uid}",le="0.25",method="GET"} 8000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/meme/{uid}",le="0.5",method="GET"} 8000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/meme/{uid}",le="0.75",method="GET"} 8000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/meme/{uid}",le="1.0",method="GET"} 8000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/meme/{uid}",le="2.5",method="GET"} 8000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/meme/{uid}",le="5.0",method="GET"} 8000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/meme/{uid}",le="7.5",method="GET"} 8000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/meme/{uid}",le="10.0",method="GET"} 8000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/meme/{uid}",le="+Inf",method="GET"} 8000.0
http_request_duration_seconds_count{endpoint="/api/v1/meme/{uid}",method="GET"} 8000.0
http_request_duration_seconds_sum{endpoint="/api/v1/meme/{uid}",method="GET"} 41.125821113586426
http_request_duration_seconds_bucket{endpoint="/api/v1/joke/{uid}",le="0.005",method="GET"} 4133.0
http_request_duration_seconds_bucket{endpoint="/api/v1/joke/{uid}",le="0.01",method="GET"} 7894.0
http_request_duration_seconds_bucket{endpoint="/api/v1/joke/{uid}",le="0.025",method="GET"} 7960.0
http_request_duration_seconds_bucket{endpoint="/api/v1/joke/{uid}",le="0.05",method="GET"} 8000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/joke/{uid}",le="0.075",method="GET"} 8000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/joke/{uid}",le="0.1",method="GET"} 8000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/joke/{uid}",le="0.25",method="GET"} 8000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/joke/{uid}",le="0.5",method="GET"} 8000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/joke/{uid}",le="0.75",method="GET"} 8000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/joke/{uid}",le="1.0",method="GET"} 8000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/joke/{uid}",le="2.5",method="GET"} 8000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/joke/{uid}",le="5.0",method="GET"} 8000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/joke/{uid}",le="7.5",method="GET"} 8000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/joke/{uid}",le="10.0",method="GET"} 8000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/joke/{uid}",le="+Inf",method="GET"} 8000.0
http_request_duration_seconds_count{endpoint="/api/v1/joke/{uid}",method="GET"} 8000.0
http_request_duration_seconds_sum{endpoint="/api/v1/joke/{uid}",method="GET"} 40.22812843322754
http_request_duration_seconds_bucket{endpoint="/api/v1/user/login",le="0.005",method="GET"} 1438.0
http_request_duration_seconds_bucket{endpoint="/api/v1/user/login",le="0.01",method="GET"} 1990.0
http_request_duration_seconds_bucket{endpoint="/api/v1/user/login",le="0.025",method="GET"} 1995.0
http_request_duration_seconds_bucket{endpoint="/api/v1/user/login",le="0.05",method="GET"} 2000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/user/login",le="0.075",method="GET"} 2000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/user/login",le="0.1",method="GET"} 2000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/user/login",le="0.25",method="GET"} 2000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/user/login",le="0.5",method="GET"} 2000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/user/login",le="0.75",method="GET"} 2000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/user/login",le="1.0",method="GET"} 2000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/user/login",le="2.5",method="GET"} 2000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/user/login",le="5.0",method="GET"} 2000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/user/login",le="7.5",method="GET"} 2000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/user/login",le="10.0",method="GET"} 2000.0
http_request_duration_seconds_bucket{endpoint="/api/v1/user/login",le="+Inf",method="GET"} 2000.0
http_request_duration_seconds_count{endpoint="/api/v1/user/login",method="GET"} 2000.0
http_request_duration_seconds_sum{endpoint="/api/v1/user/login",method="GET"} 9.320150375366211
# HELP http_request_duration_seconds_created HTTP request duration in seconds
# TYPE http_request_duration_seconds_created gauge
http_request_duration_seconds_created{endpoint="/api/v1/app-info/versions",method="GET"} 1.778548593690554e+09
http_request_duration_seconds_created{endpoint="/api/v1/app-info/metrics",method="GET"} 1.7785485943666859e+09
http_request_duration_seconds_created{endpoint="/api/v1/docs",method="GET"} 1.7785485967954128e+09
http_request_duration_seconds_created{endpoint="/api/v1/openapi.json",method="GET"} 1.778548598029489e+09
http_request_duration_seconds_created{endpoint="/api/v1/meme/{uid}",method="GET"} 1.7785486806421945e+09
http_request_duration_seconds_created{endpoint="/api/v1/joke/{uid}",method="GET"} 1.7785486945188067e+09
http_request_duration_seconds_created{endpoint="/api/v1/user/login",method="GET"} 1.778548709867564e+09
# HELP api_calls_total Total number of API calls by type
# TYPE api_calls_total counter
api_calls_total{api_type="app-info"} 65.0
api_calls_total{api_type="docs"} 1.0
api_calls_total{api_type="openapi.json"} 1.0
api_calls_total{api_type="meme"} 8000.0
api_calls_total{api_type="joke"} 8000.0
api_calls_total{api_type="user"} 2000.0
# HELP api_calls_created Total number of API calls by type
# TYPE api_calls_created gauge
api_calls_created{api_type="app-info"} 1.7785485936906946e+09
api_calls_created{api_type="docs"} 1.7785485967954996e+09
api_calls_created{api_type="openapi.json"} 1.7785485980295885e+09
api_calls_created{api_type="meme"} 1.778548680642281e+09
api_calls_created{api_type="joke"} 1.7785486945188985e+09
api_calls_created{api_type="user"} 1.7785487098676503e+09
# HELP http_errors_4xx_total Total number of 4xx HTTP errors
# TYPE http_errors_4xx_total counter
http_errors_4xx_total{endpoint="/api/v1/meme/{uid}",status_code="404"} 8000.0
http_errors_4xx_total{endpoint="/api/v1/user/login",status_code="405"} 2000.0
# HELP http_errors_4xx_created Total number of 4xx HTTP errors
# TYPE http_errors_4xx_created gauge
http_errors_4xx_created{endpoint="/api/v1/meme/{uid}",status_code="404"} 1.7785486806423042e+09
http_errors_4xx_created{endpoint="/api/v1/user/login",status_code="405"} 1.7785487098677707e+09
# HELP http_errors_5xx_total Total number of 5xx HTTP errors
# TYPE http_errors_5xx_total counter
http_errors_5xx_total{endpoint="/api/v1/joke/{uid}",status_code="500"} 2000.0
# HELP http_errors_5xx_created Total number of 5xx HTTP errors
# TYPE http_errors_5xx_created gauge
http_errors_5xx_created{endpoint="/api/v1/joke/{uid}",status_code="500"} 1.778548706303846e+09
# HELP user_logins_total Total number of user logins
# TYPE user_logins_total counter
user_logins_total 0.0
# HELP user_logins_created Total number of user logins
# TYPE user_logins_created gauge
user_logins_created 1.7785485935033152e+09
# HELP user_logins_succeed_total Total number of successful user logins
# TYPE user_logins_succeed_total counter
user_logins_succeed_total 0.0
# HELP user_logins_succeed_created Total number of successful user logins
# TYPE user_logins_succeed_created gauge
user_logins_succeed_created 1.778548593503362e+09
```
Здесь видно, что чем больше разнообразия в метках (лэйблах), 
тем больше метрик собирается и отправляется в prometheus, 
поэтому чтобы не забивать все ресурсы метриками, 
лучше не добавлять лишние метки и метрики без необходимости.

Теперь когда наше приложение способно выдавать метрики, 
соберем их при помощи prometheus.

## Настройка prometheus

В данном проекте настройки prometheus будем подтягивать в docker контейнер через volume.
В файле **prometheus/prometheus.yml** 
опишем конфигурацию как часто и откуда запрашивать метрики:
```yaml
global:
  scrape_interval: 20s
  evaluation_interval: 20s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'api'
    static_configs:
      - targets: ['api-for-monitoring:8000']
    scrape_interval: 15s
    metrics_path: '/api/v1/app-info/metrics'
```
Здесь:
- `scrape_interval: 20s` - задает интервал опроса метрик по умолчанию
- `evaluation_interval: 20s` - задает интервал опроса метрик по умолчанию
- в `scrape_configs` задаются все источники метрик и как именно их оттуда вытягивать 
  (в данном случае будут вытягиваться метрики самого prometheus и нашего бэкенда, живущего в контейнере api-for-monitoring)
- `- targets: ['localhost:9090']` - указывает на каких адресах находятся источники метрик
- `metrics_path: '/api/v1/app-info/metrics'` - указывает по какому эндпоинту можно получать метрики get запросом на указанном адресе

В **docker-compose.yml** файле prometheus будет задаваться следующим образом:
```yaml
---
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=240h'  # 10 days of history
      - '--web.enable-lifecycle'
    networks:
      - monitoring-example

networks:
  monitoring-example:

volumes:
  prometheus_data:
```
Здесь:
- мы открываем 9090 чтобы можно было делать к нему запросы извне 
  (что в данной конфигурации не прям обязательно, поскольку все контейнеры будут в одной сети)
- `./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml` - прокидываем конфиг через вольюм
- при запуске явно указываем откуда брать конфиг через `'--config.file=/etc/prometheus/prometheus.yml'`
- при запуске явно указываем где хранить полученные метрики `--storage.tsdb.path=/prometheus`
- при запуске указываем за какой период времени хранить метрики `--storage.tsdb.retention.time=240h`
  (метрики много весят, поэтому не всегда есть возможность хранить метрики за большое количество времени)
- при запуске указываем, что конфиги могут перезагружаться автоматически без перезапуска `--web.enable-lifecycle`

## Grafana

Теперь хорошо бы отобразить все накапливаемые данные.
Для этого мы можем воспользоваться таким инструментом мониторинга метрик как **grafana**.
Она позволяет объединить много метрик из разных систем на настраиваемых панелях (дашбордах).

Чтобы отображать данные, для начала необходимо задать для **grafana** откуда их будем брать.
В данном проекте 
```yaml
---
services:
  
  grafana:
    image: grafana/grafana
    container_name: grafana
    restart: unless-stopped
    environment:
#      - GF_SERVER_ROOT_URL=/grafana  # for nginx reverse proxy
      - GF_PATHS_PROVISIONING=/etc/grafana/provisioning
      - GF_AUTH_ANONYMOUS_ENABLED=false
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
#      - GF_AUTH_ANONYMOUS_ENABLED=true  # for no pass login
#      - GF_AUTH_ANONYMOUS_ORG_ROLE=Admin
      - TZ=${SYSTEM_TIMEZONE:-Europe/Moscow}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning/datasources:/etc/grafana/provisioning/datasources
      - ./grafana/provisioning/dashboards:/etc/grafana/provisioning/dashboards
    ports:
      - "3000:3000"
    networks:
      - monitoring-example

volumes:
  grafana_data:
```
Здесь:
- `GF_PATHS_PROVISIONING=/etc/grafana/provisioning` - задает путь, откуда **grafana** будет брать конфиги
- после этого конфиги (источники данных `datasources` и дашборды `dashboards`) и директория с данными **grafana** прокидываются через вольюмы:
  ```yaml
  volumes:
    - grafana_data:/var/lib/grafana
    - ./grafana/provisioning/datasources:/etc/grafana/provisioning/datasources
    - ./grafana/provisioning/dashboards:/etc/grafana/provisioning/dashboards
  ```
- задается обязательный вход по логину и паролю для админа
  ```yaml
  - GF_AUTH_ANONYMOUS_ENABLED=false
  - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
  ```
  Его можно отключить, если вместо этого прописать:
  ```yaml
  - GF_AUTH_ANONYMOUS_ENABLED=true  # for no pass login
  - GF_AUTH_ANONYMOUS_ORG_ROLE=Admin
  ```
- `TZ=${SYSTEM_TIMEZONE:-Europe/Moscow}` - устанавливает временную зону, относительно которой все будет показываться

### Настройка источников

Зададим настройку источников метрик (в нашем случае **prometheus**)
в файле **grafana/provisioning/datasources/datasources.yaml**:
```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    uid: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
```
Здесь:
- `type: prometheus` - указывает какой плагин использовать для взаимодействия с источником (тут prometheus)
- `access: proxy` - указывает, чтобы **grafana** выступала в роли прокси‑сервера.
  Т.е. все запросы от браузера пользователя к источнику данных проходят через сервер **grafana**. 
  Это безопаснее, так как учётные данные не передаются в браузер. 
  (реже ставят настройку `direct`, чтобы подключатся к источнику данных напрямую)
- `url: http://prometheus:9090` - задает адрес **prometheus**, 
  откуда будут тянуться метрики
- `isDefault: true` - указывает, что при создании новой панели на дашборде поле 'Источник данных' 
  автоматически заполнится этим источником.
- `editable: true` - разрешает редактирование через интерфейс

Подробнее см.
https://grafana.com/docs/grafana/latest/datasources/.

### Настройка дашбордов

Зададим файл настроек дашбордов **grafana/provisioning/dashboards/all.yml**:
```yaml
apiVersion: 1
providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: 'file'
    disableDeletion: false
    updateIntervalSeconds: 10
    options:
      path: '/etc/grafana/provisioning/dashboards'
```
Здесь:
- `orgId: 1` задает id организации, к которой будут привязываться дашборды 
  (1 - организация по умолчанию)
- `folder: ''` означает, что дашборды будут размещены в корневой папке (без подпапок)
- `type: 'file'` означает, что **grafana** будет искать дашборды в виде файлов в файловой системе, 
  где она запущена (можно также из гита например)
- `disableDeletion: false` означает, что если удалить дашборд из папки, 
  **grafana** автоматически удалить его из интерфейса
- `updateIntervalSeconds: 10` задает время обновления дашбордов как 10 секунд
- `path: '/etc/grafana/provisioning/dashboards'` указывает полный путь к папке, 
  где **grafana** будет искать дашборды 
  (в данном случае все .json файлы из этой папки будут загружены как дашборды)

Подробнее см.
https://grafana.com/docs/grafana/latest/visualizations/dashboards/.

### Добавление дашбордов

Пока что если мы после запуска docker-compose.yml 
(можно через `make compose_up_rebuild`) 
откроем страницу 'http://localhost:3000/dashboards', 
то там не будет ни одного дашборда
(будет только возможность войти в систему через админа с указанием заданного тобой пароля).

#### Добавление новых дашбордов

Можно создать свой новый дашборд с нуля. Для этого нужно сделать:
- нажать кнопку **New** (Новый) и в выпадающем меню выбрать **New dashboard** (Новый дашборд).
- на открывшейся странице нажать иконку **Add new element** (синий плюсик) 
  и выбрать **Panel** (Панель) для добавления первой панели.

Панель — это базовый элемент дашборда.
Она получает данные из источника и отображает их в виде 
графика, таблицы, гистограммы и т.д.

Чтобы добавить панель:

Нажми иконку «+» в верхней панели инструментов дашборда.
- В выпадающем меню выбери Visualization («Визуализация»).
- В настройках панели выбери источник данных из выпадающего списка Data source. 
  Если нужный источник ещё не добавлен, настрой его заранее.
- Напиши запрос для получения данных. 
  Формат запроса зависит от типа источника данных — например, 
  для Prometheus используется PromQL.
- Выбери тип визуализации: график, таблица, одиночное значение (Single Stat), тепловая карта и т.д.
- Настрой параметры панели: оси, легенду, цвета, временной диапазон, интервал обновления и другие опции.
- Нажми **Save** (Сохранить), чтобы добавить панель на дашборд.

Ты можешь добавить несколько панелей с разными запросами и типами визуализации — так дашборд станет информативнее.

Настройка источников данных
Перед созданием дашборда тебе нужно добавить и настроить источники данных, 
из которых будут извлекаться метрики:
- В левом меню перейди в Connections → Data sources (Соединения» → «Источники данных).
- Нажми Add data source (Добавить источник данных).
- Выбери тип источника — например, Prometheus, PostgreSQL, Loki и т.д.
- Настрой параметры подключения: укажи URL, введи учётные данные и т. п.
- Нажми **Save & test** (Сохранить и проверить), чтобы протестировать подключение.
- Учти, что добавлять и удалять источники данных 
могут только пользователи с ролью администратора организации.

Когда настроишь все панели:
- Добавь заголовок и описание для дашборда — так будет понятнее, что он показывает.
- Выбери папку для сохранения (если у тебя есть папки).
- Нажми **Save** (Сохранить).
- Нажми **Exit edit** (Выйти из редактирования), чтобы завершить работу с дашбордом.

Чтобы легче было ориентироваться лучше всего группировать графики по категориям.

Чтобы клонировать график, и не вбивать все настройки с нуля, 
можно использовать опцию **Repeat Panel**.

Старайся не перегружать дашборд, оставляя самое важное, 
чтобы на нем было легко найти нужную информацию.

#### Экспорт и импорт дашбордов

Чтобы экспортировать дашборд, открой его, 
нажми иконку **Share** в верхней части экрана и выбери **Save to file**. 
Дашборд сохранится в формате json.

Дашбор в виде json можно потом импортировать в любой проект.

Импортировать шаблон можно на странице шаблонов, нажав **New -> Import**.
В открывающейся странице можно импортировать дашборд, вставив туда его json, 
а можно импортировать по коду из всемирного хранилища дашбордов.
Посмотреть какие дашборды доступны по коду можно тут:
https://grafana.com/grafana/dashboards.
Очень советую поискать там что-то для своего проекта, 
поскольку там можно воспользоваться удобным поиском по названию шаблона (по fastapi например).

[//]: # (TODO)




[//]: # (TODO dashboard for user_logins_total, user_logins_succeed_total)

## Моделирование нагрузки через Apache Benchmark

Чтобы смоделировать простенькую нагрузку на наше приложение, 
воспользуемся утилитой **ab** (**Apache Benchmark**).

С ее помощью можно создавать большое количество запросов за короткое время.

Например, можно сделать по 10000 запросов на получение версии приложения с 10 клиентов:
```shell
ab -k -c 10 -n 10000 http://localhost:8000/api/v1/app-info/versions
```

Сделаем запросы и для остальных ручек:
```shell
# успешные запросы на получение мемов
ab -k -c 10 -n 2000 http://localhost:8000/api/v1/meme/1
ab -k -c 10 -n 2000 http://localhost:8000/api/v1/meme/2
ab -k -c 10 -n 2000 http://localhost:8000/api/v1/meme/0
# запросы на получение мемов, которые приведут к 500-й ошибке
ab -k -c 10 -n 2000 http://localhost:8000/api/v1/meme/100

# успешные запросы на получение шуток
ab -k -c 10 -n 2000 http://localhost:8000/api/v1/joke/2
ab -k -c 10 -n 2000 http://localhost:8000/api/v1/joke/0
ab -k -c 10 -n 2000 http://localhost:8000/api/v1/joke/1
# запросы на получение шуток, которые приведут к 500-й ошибке
ab -k -c 10 -n 2000 http://localhost:8000/api/v1/joke/100

# запросы на логин, которые приведут к 422-й ошибке
ab -k -c 10 -n 2000 http://localhost:8000/api/v1/user/login
```
Теперь мы набрали некоторую статистику о запросах в нашем **prometheus** модуле.

Прогнав все эти команды, 
можно будет легко оценить как метрики по разным запросам отображаются на дашбордах.

В этом приложении для удобства команды Apache Benchmark обернуты в make команду:
```shell
make ab
```
