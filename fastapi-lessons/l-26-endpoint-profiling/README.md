# Профилирование кода

Порой приложение может работать долго из-за каких-то определенных мест в коде, 
которые работают сильно медленнее, чем остальное приложение.
Такие куски кода обычно называют узкими местами или ботлнеками (bottlenecks).

Если мы хотим от них избавиться нам необходимо их сначала найти.
Например, мы можем проанализировать какие места в коде 
сколько ресурсов съедают во времени работы приложения.
Иными словами мы можем провести профилирование кода.

**Профилирование кода** - 
это процесс сбора и анализа характеристик работы программы во время её выполнения.

Зачем нужно профилирование
Основная цель — выявить ботлнеки в коде, 
чтобы целенаправленно оптимизировать производительность. 
Без профилирования оптимизация часто превращается в угадывание проблем, 
что ведёт к напрасной трате времени.

Профилирование можно применять:
- на этапе разработки при выявлении проблем с производительностью
- перед выпуском релиза для проверки стабильности
- в продакшене для мониторинга и оптимизации работающих сервисов
- при рефакторинге для оценки эффективности изменений

## Использование pyinstrument для профилирования

Зачастую для профилирования python кода на данный момент используется библиотека pyinstrument или ее производные.
Она позволяет получить информацию о количестве запусков тех или иных функций 
(обычно это называется стеком вызова или callstack), 
о том сколько какие функции в среднем выполнялись по времени (timeline), 
как хорошо утилизировались ресурсы приложения (те как много приложение простаивало бездельно), итд.

Библиотека pyinstrument позволяет сгенерировать результат профилирования в виде html страницы, 
чтобы анализировать информацию в удобном интерфейсе.

С ее момощью можно профилировать либой python код.
В этом уроке мы будем профилировать ручки нашего бэкенд приложения.

## Backend приложение для профилирования

Для начала создадим приложение, 
внутри которого под капотом будет множество вызовов функций (чтобы было что анализировать).

Зададим описание ручек нашего приложения в **src/route/some_routes.py**:
```python
from random import randint
from time import sleep

from fastapi.routing import APIRouter

from src.config import settings
from src.service.some_service import get_huge_random_number

router = APIRouter(prefix=settings.BASE_ROUTE_PATH)


@router.get('/some-complex-logic')
async def get_long_response():
    sleep(3)
    return 'Done!'


@router.get('/some-simple-logic')
async def get_fast_response():
    return 'No more calls here!'


@router.get('/endpoint-with-random-complexity')
async def get_random_time_response():
    initial_seed = 0
    for _ in range(randint(5, 1000)):
        initial_seed += get_huge_random_number(100, 200)
    output = 0
    for _ in range(int(initial_seed) % 100):
        output += get_huge_random_number(10_000, 50_000)
    return output
```
Ручку ```get_random_time_response``` мы специально сильно усложняем большим количеством вызовов, 
чтобы было интереснее анализировать.

В сервисе смоделируем абстрактную функцию, которая будет производить больше количество нагруженных вычислений:
```python
import math
from random import randint


def get_huge_random_number(seed1, seed2):
    output = 0
    for i in range(randint(seed1, seed2)):
        output += math.cos(i) * math.factorial(math.floor(41 + 40 * math.cos(i)))
    return output
```

## Middleware для профилирования

Чтобы проанализировать все процессы, 
которые будут происходить в ручке, 
добавим middleware под профилирование в **src/main.py**:
```python
import uvicorn
from fastapi import FastAPI

from src.config import settings
from src.middleware import ProfilingMiddleware
from src.route.some_routes import router

app = FastAPI(
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs",
)

app.add_middleware(ProfilingMiddleware)

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
```

В **src/config.py** зададим переменную,
которой можно будет включать/отключать профилирование 
(чтобы была возможность его отключить на проде):
```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='.env'
    )
    BASE_ROUTE_PATH: str = '/api/v1'
    ENABLE_ENDPOINT_PROFILING: bool = False


settings = Settings()
```

Сам middleware класс в **src/middleware.py** будет выглядеть следующим образом:
```python
from fastapi import Request
from fastapi.responses import HTMLResponse
from pyinstrument import Profiler
from starlette.middleware.base import BaseHTTPMiddleware

from src.config import settings


class ProfilingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, profile_initiating_query_param: str = 'profile'):
        super().__init__(app)
        self.profile_initiating_query_param = profile_initiating_query_param

    async def dispatch(self, request: Request, call_next):
        profiling = request.query_params.get(self.profile_initiating_query_param, False)
        if profiling and settings.ENABLE_ENDPOINT_PROFILING:
            profiler = Profiler()
            profiler.start()
            await call_next(request)
            profiler.stop()
            return HTMLResponse(profiler.output_html())
        else:
            return await call_next(request)
```
Здесь:
- мы для каждого запроса получаем query параметр запроса
(```profiling = request.query_params.get(self.profile_initiating_query_param, False)```) 
с помощью которого мы понимаем нужно ли нам выполнять саму ручку и отдавать ее ответ, 
или же мы хотим получить анализ ее работы от pyinstrument
- выдаем анализ работы ручки, 
если клиент добавил параметр профилирования в ручку (получили его в переменную profiling) 
и профилирование включено в настройках приложения
- в обратном случае выдаем просто ответ самой ручки так, 
как если бы никакого профайлера не было

Теперь мы можем вызвать ручку с query параметром profile=true и получить отчет о работе приложения.
Так например для анализа работы ручки '/endpoint-with-random-complexity'
можно просто открыть в браузере ссылку
http://localhost:8000/api/v1/endpoint-with-random-complexity?profile=true.

На этой странице мы сможем увидеть сколько раз какой метод в итоге вызвался, 
и сколько времени вызов каждого метода по итогу занял.

При этом мы можем увидеть, 
что при работе этой ручки программа утилизирует почти 100% процессора.

Если же мы запустим ручку, в которой мы используем ```sleep```, 
то мы увидим, что ресурсы процессора почти не утилизировались.
Те. мы можем как находить куски кода, 
где программа работает слишком долго, 
так и места, где программа просто ждет чего-то 
(например какого-нибудь ответа в синхронном режиме).

Также мы написали здесь лишь middleware обертку для pyinstrument, 
так-то с его помощью можно профилировать любые куски кода.

Подробнее о pyinstrument можно почитать тут:
https://pyinstrument.readthedocs.io/en/latest/guide.html.
