from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapter.db.session import get_session
from src.scheme.user import UserCreate, UserFromDB, UserLogin
from src.service.user import UserService

router = APIRouter()


@router.post('/register')
async def create_user(data: UserCreate, db_session: AsyncSession = Depends(get_session)) -> UserFromDB:
    new_user = await UserService.create_user(data, db_session)
    return new_user.serialize()


@router.post('/login')
async def login(body: UserLogin, response: Response, db_session: AsyncSession = Depends(get_session)) -> str:
    return await UserService.login(body, response, db_session)


@router.post("/logout")
async def logout(response: Response) -> str:
    return await UserService.logout(response)
