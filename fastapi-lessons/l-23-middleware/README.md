# Middleware

**Middleware** - это слой приложения, 
отвечающий за операции с запросами перед их основной обработкой.
В данном уроке мы рассмотрим операции перед обработкой запросов в бэкенде.

Этот слой используют, например, 
чтобы ограничивать доступ к определенным доменам, 
с которых приходят запросы (CORS), 
или же для ограничения количества возможных запросов к бэкенду (rate limiting) итд.

Зачастую это делается с помощью конкретных библиотек (), 
но порой необходимо прописать что-то специфическое самим.
Поэтому в данном уроке мы рассмотрим как в принципе работает middleware, 
и как написать его самим с использованием функционала fastapi (starlette).
В дальнейших же уроках мы рассмотрим 
популярные специализированные middleware библиотеки 
для решения конкретных часто встречаемых задач.

## Простейший способ написания middleware

Напишем простую middleware функцию, 
которая будет ограничивать количество запросов к определенной ручке, 
если они приходят от одного и того же адреса. 

Для начала добавим две ручки в **src/route/some_routes.py**:
```python
from src.config import settings

router = APIRouter(prefix=settings.BASE_ROUTE_PATH)

@router.get('/hello')
async def hello_world():
    return 'Hi mam!'


@router.get('/only-one-chance')
async def will_be_blocked_in_middleware():
    return 'No more calls here!'
```
Далее будем делать так, 
чтобы наш middleware разрешал делать 
сколько угодно запросов к ручке '/hello', 
но ручку '/only-one-chance' разрешал дергать 
только один раз с одного и того же адреса.

Добавим в **src/main.py** функцию, 
которая будет способна делать какие-то действия до и после каждого запроса:
```python
from typing import Callable

@app.middleware('http')
async def handle_spam(request: Request, call_next: Callable):
    print('Вылезает до запроса')
    response = await call_next(request)
    print('Вылезает осле запроса')
    return response
```
Здесь:
- ```@app.middleware('http')``` - декоратор, 
заставляющий эту функцию запускаться при появлении новых запросов 
и вызывающую основную обработку запросов в себе.
- ```request: Request``` - объект входящего запроса
- ```call_next: Callable``` - функция, которая может вызвать основную обработку запроса
- ```response = await call_next(request)``` - вызов основной обработки запроса
- ```return response``` - передача ответа пользователю

Теперь добавим сюда логику ограничения запросов для пользователей (по адресам):
```python
blocked_addresses = []

@app.middleware('http')
async def handle_spam(request: Request, call_next: Callable):
    client_address = request.client.host
    print(f'call from {client_address}')
    if client_address in blocked_addresses:
        return Response(status_code=429, content="Вы отправляли запрос на этот адрес!")
    if '/only-one-chance' in str(request.url):  # если это запрос к той самой ручке, то блокируем адрес
        blocked_addresses.append(client_address)
    # для самой обработка запроса (вызов функции, к которой прикреплен соответствующий декоратор):
    response = await call_next(request)
    return response
```
Здесь:
- ```blocked_addresses = []``` - создание списка адресов, 
которые уже сделали запросы к нашей одноразовой ручке
- ```client_address = request.client.host``` - получение адреса от пользователя
- ```return Response(status_code=429, content="Вы отправляли запрос на этот адрес!")``` - 
отправка ошибки "Too many requests" 
(поскольку этот код в ```if client_address in blocked_addresses:```, 
то он вызовется только если от адреса уже был запрос на искомую ручку)
- ```if '/only-one-chance' in str(request.url):``` - 
проверяем, на одноразовую ручку пришел запрос или нет 
(если да, то добавляем адрес в список тех, 
кто уже посещал эту ручку с помощью ```blocked_addresses.append(client_address)``)

Таким образом приложение будет разрешать делать
сколько угодно запросов к ручке '/hello',
но ручку '/only-one-chance' можно будет дернуть
только один раз с одного и того же адреса.


## Описание middleware через классы (более чистый способ)

Напишем в **src/middleware.py** простой класс для описания middleware, 
который пока просто будет содержать структуру
(пока ничего дополнительного не делает):
```python
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class MyVeryOwnMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        
        # тут можно делать операции перед непосредственной обработкой запроса
        
        response = await call_next(request)

        # тут можно делать операции с ответом
        
        return response
```
Здесь мы наследуемся от класса ```BaseHTTPMiddleware```, 
в котором есть метод ```def dispatch(self, request: Request, call_next)```.
Этот метод ```dispatch``` будет в дальнейшем вызываться при приходе запроса на бэк. 
В нем мы точно также обязаны вызвать ```response = await call_next(request)```,
чтобы запустить обработку запроса 
(те. та часть, которую мы все время описывали без middleware).

Чтобы бэкенд приложение сам вызывало метод ```dispatch``` при приходе запроса, 
подключим наш middleware класс к нашему fastapi приложению в **src/main.py**:
```python
from src.middleware import MyVeryOwnMiddleware

app.add_middleware(MyVeryOwnMiddleware)
```

Теперь перепишем логику нашего middleware 
(который описывался через функцию) 
в наш новый класс.

Теперь мы можем хранить все данные в атрибутах объекта этого класса, 
и задавать часть из них при создании данного объекта 
(например количество раз, которое пользователь сможет дерагать ручку '/only-one-chance').

Тогда описание нашего middleware класса в **src/middleware** 
будет выглядеть следующим образом:
```python
from collections import defaultdict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class MyVeryOwnMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_before_block: int):
        super().__init__(app)
        self.requests_before_block = requests_before_block
        self.blocked_addresses = defaultdict(int)

    async def dispatch(self, request: Request, call_next):
        # делаем что-то до основной обработки запроса
        # например проверяем доступность ручки для конкретного адреса
        client_address = request.client.host
        print(f'call from {client_address}')
        if '/only-one-chance' in str(request.url):  # если это запрос к той самой ручке, то прибавляем счетчик адрес
            self.blocked_addresses[client_address] += 1
            if self.blocked_addresses[client_address] > self.requests_before_block:
                return Response(status_code=429, content="Вы отправляли запрос на этот адрес!")

        # для самой обработка запроса (вызов функции, к которой прикреплен соответствующий декоратор):
        # те делаем сам запрос и получаем результат
        response = await call_next(request)

        # пост-запросные штуки
        # например прилепляем хэдеры
        response.headers['CallsMade'] = f'{self.requests_before_block}'

        return response
```
Здесь:
- в конструкторе задается число попыток запроса, которые можно сделать с каждого адреса (```requests_before_block```)
- в начале метода ```dispatch``` высчитывается сколько раз с текущего адреса был совершен запрос, 
и если это число превысило переменную```requests_before_block```, выдается ошибка 429 (слишком много запросов)
- после отработки самой ручки (```response = await call_next(request)```) 
в хэдер полученного ответа добавляется значение количества совершенных вызовов
(```response.headers['CallsMade'] = f'{self.requests_before_block}'```)

Тогда подключение к нашему fastapi приложению в **src/main.py** будет выглядеть:
```python
app.add_middleware(MyVeryOwnMiddleware, requests_before_block=3)
```

Теперь ручку **/only-one-chance** можно вызвать только то количество раз, 
которое мы задаем при инициализации middleware класса 
(ну и плюс количество оставшихся запросов автоматом будет пропихиваться пользователю в хэдерах ответа).
