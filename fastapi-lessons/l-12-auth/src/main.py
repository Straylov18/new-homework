import uvicorn
from fastapi import FastAPI, Response, HTTPException, Depends
from fastapi.routing import APIRouter
from pydantic import EmailStr

from src.auth import create_access_token, get_token, get_token_payload_if_valid

BASE_ROUTE_PATH = "/api/v1"

app = FastAPI(
    openapi_url=f"{BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{BASE_ROUTE_PATH}/docs",
)

router = APIRouter(prefix=BASE_ROUTE_PATH)

users = [
    {
        'id': 0,
        'email': 'shaytan@cheburnetomail.ru',
        'password': '1',
    },
    {
        'id': 1,
        'email': 'admin@cheburnetomail.ru',
        'password': '1235',
    },
]


@router.get('/login')
async def login(email: EmailStr, password: str, response: Response):
    for u in users:
        if u["email"] == email and u["password"] == password:
            jwt_token_data = {"email": email}
            jwt_token = create_access_token(jwt_token_data)
            response.set_cookie("access_token", jwt_token)
            return "Успешный вход!"
    return "Пользователь не найден:("


@router.get('/hello')
async def hello_user(token: str = Depends(get_token)):
    payload = get_token_payload_if_valid(token)

    user_id: str = payload.get('email')
    if not user_id:
        raise HTTPException(403, "Нет такого пользователя! Обманщик!")

    return f"Hi, {payload.get('email')}!"


@router.post("/logout/")
async def logout_user(response: Response):
    response.delete_cookie(key="access_token")
    return {'message': 'Пользователь вышел из системы. Бб, дружище!'}


app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
