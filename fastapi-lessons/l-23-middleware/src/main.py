from typing import Callable

import uvicorn
from fastapi import FastAPI, Request, Response

from src.config import settings
from src.route.some_routes import router

app = FastAPI(
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs",
)

## примитивный способ
# blocked_addresses = []
#
#
# @app.middleware('http')
# async def handle_spam(request: Request, call_next: Callable):
#     client_address = request.client.host
#     print(f'call from {client_address}')
#     if client_address in blocked_addresses:
#         return Response(status_code=429, content="Вы отправляли запрос на этот адрес!")
#     if '/only-one-chance' in str(request.url):  # если это запрос к той самой ручке, то блокируем адрес
#         blocked_addresses.append(client_address)
#     # для самой обработка запроса (вызов функции, к которой прикреплен соответствующий декоратор):
#     response = await call_next(request)
#     return response

from src.middleware import MyVeryOwnMiddleware

app.add_middleware(MyVeryOwnMiddleware, requests_before_block=3)

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
