from fastapi import APIRouter, Response

from src.scheme.user import UserCreate, UserFromDB, UserLogin
from src.service.user import UserService

router = APIRouter()


@router.post('/register')
async def create_user(data: UserCreate) -> UserFromDB:
    new_user = await UserService.create_user(data)
    return new_user.serialize()


@router.post('/login')
async def login(body: UserLogin, response: Response) -> str:
    return await UserService.login(body, response)


@router.post("/logout")
async def logout(response: Response) -> str:
    return await UserService.logout(response)
