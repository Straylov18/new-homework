from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapter.db.session import get_session
from src.scheme.user_post import UserPostCreate, UserPostFromDB
from src.service.user_post import UserPostService
from src.utils.auth import get_token

router = APIRouter()


@router.get('/list')
async def get_user_posts_list(db_session: AsyncSession = Depends(get_session)) -> list[UserPostFromDB]:
    return [up.serialize() for up in await UserPostService.get_users_list(db_session)]


@router.post('/')
async def create_user_post(data: UserPostCreate,
                           token: str = Depends(get_token),
                           db_session: AsyncSession = Depends(get_session)) -> UserPostFromDB:
    new_user_post = await UserPostService.create_user_post(data, token, db_session)
    return new_user_post.serialize()
