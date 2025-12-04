from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.user_post import UserPost
from src.scheme.user_post import UserPostCreate
from src.service.user import UserService
from src.utils.auth import get_token_payload_if_valid


class UserPostService:

    @staticmethod
    async def create_user_post(data: UserPostCreate, token: str, db_session: AsyncSession) -> UserPost:
        token_payload = get_token_payload_if_valid(token)
        user = await UserService.get_user_by_email(token_payload['email'], db_session)
        if user.uid != data.user_uid:
            raise HTTPException(400, "вам можно создавать только от своего имени!")
            # лучше конечно делать свои кастомные исключения на базе дефолтных и выносить их в отдельный слой
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
