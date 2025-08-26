from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.schemes.user import UserCreate, UserFromDB
from src.models.user import User
from src.db.session import get_session

router = APIRouter()


@router.get('/list')
async def get_users_list(db_session: AsyncSession = Depends(get_session)) -> list[UserFromDB]:
    query_result = await db_session.execute(select(User))
    return query_result.scalars().all()


@router.post('/')
async def create_user(body: UserCreate, db_session: AsyncSession = Depends(get_session)) -> UserFromDB:
    new_user = User(name=body.name, email=body.email)
    db_session.add(new_user)
    await db_session.commit()
    return new_user
