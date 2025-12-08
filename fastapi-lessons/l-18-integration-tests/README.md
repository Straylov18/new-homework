# Интеграционные тесты

Unit тесты конечно хороши своей скоростью написания, быстротой работы и простотой, 
но они не дают возможность полноценно проверить 
как данный модель приложения будет взаимодействовать 
с остальными модулями.
Для этого обычно пишут так называемые интеграционные тесты, 
которые либо моделируют взаимодействие с другим модулем, 
либо запускают его и полноценно проверяют как они обмениваются информацией.

Интеграционные тесты в отличие от unit тестов:
- сложнее в написании
- дольше работают
- имеют большее покрытие 
(что с одной стороны удобно, их нужно меньше для полного покрытия кода, 
однако если такой тест выдает ошибку, сложнее понять причину проблемы)

Поэтому таких тестов пишут меньше по количеству, и обычно их пишут уже после unit тестов, 
однако они тоже необходимы и без них большое количество ошибок не будет отлавливаться.

В рамках данного урока мы рассмотрим как проверить, 
правильно отрабатывает ли ручка при взаимодействии с клиентской частью приложения 
(те. ее работу от вызова до обработки в сервисе).

## Проект

Сам проект скопируем из прошлого урока.

## Тесты с запросами (синхронно)

Чтобы проверять дополнительно, как отрабатывает слой роутеров
(правильные ли валидации pydantic, правильно ли вызываются сервисы итд.), 
можно проверять результаты отправки запросов на бэкенд.
Для этого создадим тестовый клиент (пока синхронный), 
с помощью которого будем дергать ручки 

Такой интеграционный тест для ручки **/compare-colors** 
тогда будет выглядеть следующим образом:
```python
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

def test_compare_colors():
    response = client.get('/api/v1/math/compare-colors', params={'r': 1, 'g': 2, 'b': 300})
    assert response.json() == 'blue'
    assert response.status_code == 200
```
Здесь:
- ```client = TestClient(app)``` - создаем клиент, 
который будет способен дергать ручки нашего бэкенд приложения
- ```response = client.get('/api/v1/math/compare-colors', params={'r': 1, 'g': 2, 'b': 300})``` - 
делаем запрос на ручку **/compare-colors** с query параметрами, 
заданными в **params**, и получаем ответ
- ```assert response.json() == 'blue'``` - сравниваем тело ответа
- ```assert response.status_code == 200``` - сравниваем статус ответа

Сделаем подобные интеграционные тесты с запросами для остальных ручек.

Для тестов в **test_divide_and_conquer.py**:
```python
import pytest

from src.main import app

from fastapi.testclient import TestClient

client = TestClient(app)


def test_divide_and_conquer():
    response = client.get('/api/v1/math/divide_and_conquer',
                          params={'num': 8, 'denum': 4})
    assert response.json() == "conquered 2 times"
    assert response.status_code == 200

    response = client.get('/api/v1/math/divide_and_conquer',
                          params={'num': 12, 'denum': 2})
    assert response.json() == "conquered 6 times"
    assert response.status_code == 200


def test_divide_and_conquer_exception():
    with pytest.raises(Exception, match="denum must not be 0!"):
        response = client.get('/api/v1/math/divide_and_conquer',
                              params={'num': 5, 'denum': 0})
        assert response.json() == "denum must not be 0!"
        assert response.status_code == 500
```

Для тестов в **test_factorial.py**:
```python
import pytest
import math

from src.main import app

from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.mark.parametrize("number", [0, 1, 2, 3, 100])
def test_factorial_using_std_lib(number):
    response = client.get('/api/v1/math/factorial', params={'n': number})
    assert response.json() == math.factorial(number)
    assert response.status_code == 200


@pytest.mark.parametrize("number, factorial_result", [
    (0, 1),
    (1, 1),
    (2, 2),
    (3, 6),
    (25, 15511210043330985984000000),
    # (arg1_value, arg2_value),
    # ...
], ids=["проверка 0", "проверка 1", "проверка 2", "проверка 3", "проверка очень большого числа"])
def test_factorial_using_precalculated_values(number, factorial_result):
    response = client.get('/api/v1/math/factorial', params={'n': number})
    assert response.json() == factorial_result
    assert response.status_code == 200
```

## Тесты с запросами (асинхронно)

Однако такие вызовы ручек являются синхронными. 
Приложение же у нас может работать асинхронно, 
и порой нам важно проверить асинхронность его работы.
Те. порой необходимо написать тест, 
в котором несколько вызовов ручек будут обрабатываться асинхронно.

Для этого можно использовать асинхронный тестовый клиент.

Установим необходимые для этого библиотеки:
```shell
poetry add pytest-asyncio httpx
```

Перепишем тесты ручки **/compare-colors** с использованием асинхронного клиента:
```python
import pytest
from httpx import AsyncClient, ASGITransport

async_client = AsyncClient(
    transport=ASGITransport(app=app),
    base_url='http://test'
)

@pytest.mark.asyncio  # чтобы тест вызывался асинхронно
async def test_compare_colors_async():
    async with async_client as ac:
        response = await ac.get('/api/v1/math/compare-colors', params={'r': 1, 'g': 2, 'b': 300})
        assert response.json() == 'blue'
        assert response.status_code == 200
```
Здесь:
- при создании ```AsyncClient``` мы передаем fastapi приложение нашего бэкенда 
через ```transport=ASGITransport(app=app)```
- указываем базовую ссылку ```base_url='http://test'```, 
на которой будет под капотом доступен наш бэкенд в тестах 
(это обязательный параметр ```AsyncClient```, но выполнение тестов от нее в нашем случае не зависит, 
так что можно придумать любой base_url)
- необходимо добавлять декоратор ```@pytest.mark.asyncio``` 
чтобы функция теста могла выполняться в асинхронном режиме
- сам вызов ручки мы делаем внутри вызова контекстного менеджера, 
чтобы в случае ошибок все корректно отрабатывалось: ```async with async_client as ac:```

Поскольку для каждого интеграционного теста 
в таком случае необходимо обращаться к тестовому клиенту, 
их удобнее всего описывать в одном месте при помощи специального механизма фиксаций тестов.
Это мы рассмотрим в следующем уроке.
