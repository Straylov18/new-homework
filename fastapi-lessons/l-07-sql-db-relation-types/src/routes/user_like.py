from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.schemes.user_like import UserLikeCreate, UserLikeFromDB
from src.models.user_like import UserLike
from src.db.session import engine, get_session

router = APIRouter()


@router.get('/list')
async def get_user_likes_list(db_session: AsyncSession = Depends(get_session)) -> list[UserLikeFromDB]:
    query_result = await db_session.execute(select(UserLike))
    return [u.serialize() for u in query_result.scalars().all()]


@router.post('/')
async def create_user_like(data: UserLikeCreate, db_session: AsyncSession = Depends(get_session)) -> UserLikeFromDB:
    new_user_like = UserLike(**data.model_dump(exclude_unset=True))
    # new_user_like = UserLike(user_uid=data.user_uid, user_post_uid=data.user_post_uid)  # создание без model_dump
    db_session.add(new_user_like)
    await db_session.commit()
    return new_user_like.serialize()
