# Fixtures

Чтобы не запускать одинаковые куски кода для подготовки среды окружения, 
в тестах часто используются так называемые fixture (фикстуры).

**Fixture (фикстура)** - 
это заранее подготовленное состояние окружения тестирования, 
которое требуется для гарантии повторяемости теста.

Фикстурой может быть набор объектов, 
код для подготовки базы данных, определённых файлов, 
настройки соединений и тд.

## Проект

Сделаем приложение, которое будет получать один или несколько цветов 
и говорить доминантную часть цвета/цветов.

Опишем схему для удобной работы с цветом в **src/scheme/color.py**:
```python
from pydantic import BaseModel, Field

class Color(BaseModel):
    r: int = Field(description="Red part of a color", default=0)
    g: int = Field(description="Green part of a color", default=0)
    b: int = Field(description="Blue part of a color", default=0)
```

Опишем ручки в **/src/route/colors_comparison.py**
```python
from fastapi import APIRouter

from src.service.colors_comparison import get_dominant_color
from src.scheme.color import Color

router = APIRouter()


@router.get('/compare-colors')
async def compare_colors(r: int, g: int, b: int):
    return get_dominant_color(r, g, b)


@router.post('/compare-colors-list')
async def compare_colors_list(body: list[Color]) -> list[str]:
    return [get_dominant_color(**dict(c)) for c in body]
```

Прикрутим этот роутер в **src/main.py**:
```python
import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

from src.config import settings
from src.route.colors_comparison import router as color_router

app = FastAPI(
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs",
)

router = APIRouter(prefix=settings.BASE_ROUTE_PATH)

router.include_router(color_router, prefix='/colors', tags=['colors'])

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
```

Функцию получения доминантной части цвета возьмем из предыдущего урока.

Напишем для этого приложения простой интеграционный тест, 
используя асинхронный клиент:
```python
import pytest
from httpx import AsyncClient, ASGITransport

from src.main import app


@pytest.mark.asyncio
async def test_compare_colors_red():
    async_client = AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test'
    )
    async with async_client as ac:
        response = await ac.get('/api/v1/colors/compare-colors', 
                                params={'r': 100, 'g': 2, 'b': 3})
        assert response.json() == 'red'
        assert response.status_code == 200
```

## Fixture

Создание фикстуры в Pytest осуществляется с помощью декоратора ```@pytest.fixture()```. 
Функция может возвращать значение 
(например, тестовые данные, объект) 
или просто выполнять какие-то действия по настройке.
Её задача - подготовить всё необходимое перед запуском теста 
(фаза «Arrange» в классической структуре Arrange-Act-Assert) и, 
при необходимости, выполнить очистку ресурсов после его завершения (фаза «Teardown»).

Принцип работы
- Тестовая функция «запрашивает» фикстуру, 
указывая её имя в качестве одного из своих аргументов. 
Pytest автоматически обнаруживает это, 
выполняет соответствующую функцию-фикстуру перед запуском теста и 
передаёт возвращаемое ею значение в тест в качестве этого аргумента.
- Результат выполнения фикстуры 
(то, что она возвращает) передаётся в тест как аргумент.
- Если нужно выполнить какие-то действия после того, 
как тест завершился 
(например, закрыть соединение с базой данных или удалить временный файл), 
в фикстуре используется yield. 
Код до yield выполняется перед тестом (setup), 
а код после yield — после теста (teardown).

```python
import pytest
from httpx import AsyncClient, ASGITransport

from src.main import app


@pytest.fixture
def red_color_params():
    return {'r': 100, 'g': 2, 'b': 3}


@pytest.mark.asyncio
async def test_compare_colors_red(red_color_params):
    async_client = AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test'
    )
    async with async_client as ac:
        response = await ac.get('/api/v1/colors/compare-colors', 
                                params=red_color_params)
        assert response.json() == 'red'
        assert response.status_code == 200
```

Таким же образом мы можем использовать другую fixture, 
прокинув ее в другой тестовый метод:
```python
@pytest.fixture
def green_color_params():
    return {'r': 1, 'g': 200, 'b': 3}


@pytest.mark.asyncio
async def test_compare_colors_green(green_color_params):
    async_client = AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test'
    )
    async with async_client as ac:
        response = await ac.get('/api/v1/colors/compare-colors',
                                params=green_color_params)
        assert response.json() == 'green'
        assert response.status_code == 200
```

Также можно прокидывать несколько fixture в одну тестовую функцию.
Напишем тест для ручки обработки списка цветов:
```python
pytest.mark.asyncio
async def test_compare_colors_list(red_color_params, green_color_params, blue_color_params):
    async_client = AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test'
    )
    colors_list = [red_color_params, green_color_params, blue_color_params]
    async with async_client as ac:
        response = await ac.post('/api/v1/colors/compare-colors-list',
                                 json=colors_list)
        assert response.json() == ['red', 'green', 'blue']
        assert response.status_code == 200
```

## Использование клиента как fixture

Поскольку мы везде используем асинхронный клиент, 
почему бы нам и его не вынести как fixture:
```python
@pytest.fixture
def async_client():
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test'
    )


@pytest.mark.asyncio
async def test_compare_colors_red(async_client, red_color_params):
    async with async_client as ac:
        response = await ac.get('/api/v1/colors/compare-colors',
                                params=red_color_params)
        assert response.json() == 'red'
        assert response.status_code == 200
```

Клиенты для отправки запросов, общения с бд итд. обычно выносят как отдельные fixture.

## Классы тестирования

Чтобы не прокидывать конфигурировать кучу похожих тестовых функций по отдельности, 
их очень часто оборачивают в тестовые классы, 
чтобы применять настройки сразу ко многим функциям.

Название тестового класса должно начинаться с "Test". 

Создадим класс для тестирования наших ручек с цветами 
и запихнем в него все наши тестовые методы:
```python
class TestColors:
    @pytest.mark.asyncio
    async def test_compare_colors_red(self, async_client, red_color_params):
        async with async_client as ac:
            response = await ac.get('/api/v1/colors/compare-colors',
                                    params=red_color_params)
            assert response.json() == 'red'
            assert response.status_code == 200
    
    ... остальные методы
```

Теперь мы можем удобнее работать с тестами из этого класса, 
например запускать их:
```shell
poetry run pytest tests/test_colors.py::TestColors
```

Теперь мы также можем заставлять какие-то фикстуры выполнять 
перед этим обработкой этого тестового класса 
(ведь фикстуры могут ничего не возвращать, а просто выполнять какие-то действия при вызове).
Для этого мы будем перед классом писать специальный декоратор "@pytest.mark.usefixtures":
```python
@pytest.fixture
def before_colors_test():
    print("will be done before starting colors test")


@pytest.mark.usefixtures("before_colors_test")
class TestColors:
    ...
```

## Вынесение fixture в conftest.py

Если в корневой папке тестов (**tests**) создать файл **conftest.py**, 
то pytest будет запускать его каждый раз перед запуском тестов.
Поэтому какие-то настроки, используемые всеми тестами можно положить именно в него, 
например fixture клиента:
```python
from httpx import AsyncClient, ASGITransport

from src.main import app


@pytest.fixture
def async_client():
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test'
    )
```
Тогда ее не обязательно будет прописывать в других местах, 
поскольку pytest сам сканирует нужные fixture.

### Дочерние conftest.py файлы

Если в папке с тестами будет подпапка, 
в ней можно будет задать свой **conftest.py**, 
влияние которого будет распространяться только на эту папку.

Поскольку тесты принято разбивать на папки как минимум по типу тестов (unit, integration, e2e, итд.), 
перенесем наши интеграционные тесты в папку **integration_tests** 
(те. **tests/integration_tests/test_colors.py**).

Тогда фикстуры для этих тестов тоже можно вынести в **tests/integration_tests/conftest.py**:
```python
import pytest


@pytest.fixture
def red_color_params():
    return {'r': 100, 'g': 2, 'b': 3}


@pytest.fixture
def green_color_params():
    return {'r': 1, 'g': 200, 'b': 3}


@pytest.fixture
def blue_color_params():
    return {'r': 1, 'g': 2, 'b': 300}
```

Тогда фикстуры в наших интеграционных тестах 
будут подтягиваться из глобального **conftest.py** 
и локального для интеграционных тестов **conftest.py**. 
