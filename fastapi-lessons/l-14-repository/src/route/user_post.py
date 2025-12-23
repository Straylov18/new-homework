from fastapi import APIRouter, Depends

from src.scheme.user_post import UserPostCreate, UserPostFromDB
from src.service.user_post import UserPostService
from src.utils.auth import get_token

router = APIRouter()


@router.get('/list')
async def get_user_posts_list() -> list[UserPostFromDB]:
    return [up.serialize() for up in await UserPostService.get_user_posts_list()]


@router.post('/')
async def create_user_post(data: UserPostCreate,
                           token: str = Depends(get_token)) -> UserPostFromDB:
    new_user_post = await UserPostService.create_user_post(data, token)
    return new_user_post.serialize()
