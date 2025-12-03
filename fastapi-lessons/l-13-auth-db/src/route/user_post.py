from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapter.db.session import get_session
from src.scheme.user_post import UserPostCreate, UserPostFromDB
from src.service.user_post import UserPostService

router = APIRouter()


@router.get('/list')
async def get_user_posts_list(db_session: AsyncSession = Depends(get_session)) -> list[UserPostFromDB]:
    return [up.serialize() for up in await UserPostService.get_users_list(db_session)]


@router.post('/')
async def create_user_post(data: UserPostCreate, db_session: AsyncSession = Depends(get_session)) -> UserPostFromDB:
    # TODO get user_uid from token
    return await UserPostService.create_user(data, db_session).serialize()
