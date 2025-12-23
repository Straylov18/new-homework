from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.user_post import UserPost
from src.scheme.user_post import UserPostCreate
from src.service.user import UserService
from src.container.repository import repository_container
from src.utils.auth import get_token_payload_if_valid


class UserPostService:

    @staticmethod
    async def create_user_post(data: UserPostCreate, token: str) -> UserPost:
        token_payload = get_token_payload_if_valid(token)
        user = await repository_container.user_repository().get_one(email=token_payload['email'])
        if user.uid != data.user_uid:
            raise HTTPException(400, "вам можно создавать только от своего имени!")
            # лучше конечно делать свои кастомные исключения на базе дефолтных и выносить их в отдельный слой
        new_user_post = await repository_container.user_post_repository().add_one(data.model_dump(exclude_unset=True))
        return new_user_post

    @staticmethod
    async def get_user_post_by_uid(uid: UUID4) -> UserPost:
        user_post = await repository_container.user_post_repository().get_one(uid=uid)
        if not user_post:
            raise HTTPException(404, "нету такого поста")
        return user_post

    @staticmethod
    async def get_user_posts_list() -> list[UserPost]:
        user_posts = await repository_container.user_post_repository().get_list()
        return user_posts
