from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.schemes.user_post import UserPostCreate, UserPostFromDB
from src.models.user_post import UserPost
from src.db.session import engine, get_session

router = APIRouter()


@router.get('/list')
async def get_user_posts_list(db_session: AsyncSession = Depends(get_session)) -> list[UserPostFromDB]:
    query_result = await db_session.execute(select(UserPost))
    return [u.serialize() for u in query_result.scalars().all()]


@router.post('/')
async def create_user_post(data: UserPostCreate, db_session: AsyncSession = Depends(get_session)) -> UserPostFromDB:
    new_user_post = UserPost(number_of_updates=1, **data.model_dump(exclude_unset=True))
    # new_user_post = UserPost(title=data.title, text=data.text, user_uid=data.user_uid)  # создание без model_dump
    db_session.add(new_user_post)
    await db_session.commit()
    return new_user_post.serialize()
