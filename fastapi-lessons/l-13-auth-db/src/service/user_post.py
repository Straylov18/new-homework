from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.user_post import UserPost
from src.scheme.user_post import UserPostCreate


class UserPostService:

    @staticmethod
    async def create_user_post(data: UserPostCreate, db_session: AsyncSession) -> UserPost:
        new_user_post = UserPost(**data.model_dump(exclude_unset=True))
        db_session.add(new_user_post)
        await db_session.commit()
        await db_session.refresh(new_user_post)
        return new_user_post

    @staticmethod
    async def get_user_post_by_uid(uid: UUID4, db_session: AsyncSession) -> UserPost:
        query = await db_session.execute(select(UserPost).where(UserPost.uid == uid))
        user_post = query.scalar_one_or_none()
        if not user_post:
            raise HTTPException(404, "нету такого поста")
        return user_post

    @staticmethod
    async def get_user_posts_list(db_session: AsyncSession) -> list[UserPost]:
        query_result = await db_session.execute(select(UserPost))
        return query_result.scalars().all()
