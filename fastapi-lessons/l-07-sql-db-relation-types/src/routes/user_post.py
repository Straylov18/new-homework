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
async def create_user_post(body: UserPostCreate, db_session: AsyncSession = Depends(get_session)) -> UserPostFromDB:
    new_user_post = UserPost(title=body.title, text=body.text, user_uid=body.user_uid)
    db_session.add(new_user_post)
    await db_session.commit()
    return new_user_post.serialize()
