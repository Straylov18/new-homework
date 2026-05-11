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

[//]: # (TODO middleware)

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

# --- joke / meme endpoints ---

joke_responses_total = Counter(
    'joke_get_total',
    'Total number of GET requests for "/joke" endpoints',
    registry=RegistryContainer.registry()
)

meme_responses_total = Counter(
    'meme_get_total',
    'Total number of GET requests for "/meme" endpoints',
    registry=RegistryContainer.registry()
)
```
Здесь в качестве метрик собираются:
- `user_logins_total` - общее количество попыток входа в систему
- `user_logins_succeed_total` - общее количество успешных входов в систему
- `joke_responses_total` - общее количество запросов на получение шуток
- `meme_responses_total` - общее количество запросов на получение мемов

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

Таким образом 


[//]: # (TODO)


Подробнее см.
https://grafana.com/docs/grafana/latest/datasources/


[//]: # (TODO dashboard for user_logins_total, user_logins_succeed_total, joke_responses_total, meme_responses_total)
