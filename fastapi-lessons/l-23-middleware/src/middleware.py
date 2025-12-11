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
