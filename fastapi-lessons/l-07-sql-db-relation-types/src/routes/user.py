from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.schemes.user import UserCreate, UserFromDB
from src.models.user import User
from src.db.session import engine, get_session

router = APIRouter()


@router.get('/list')
async def get_users_list(db_session: AsyncSession = Depends(get_session)) -> list[UserFromDB]:
    query_result = await db_session.execute(select(User))
    return [u.serialize() for u in query_result.scalars().all()]


@router.post('/')
async def create_user(data: UserCreate, db_session: AsyncSession = Depends(get_session)) -> UserFromDB:
    new_user = User(**data.model_dump(exclude_unset=True))
    # new_user = User(name=data.name, email=data.email)  # создание без model_dump
    db_session.add(new_user)
    await db_session.commit()
    return new_user.serialize()
