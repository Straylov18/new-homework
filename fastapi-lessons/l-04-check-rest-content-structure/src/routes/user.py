from fastapi import APIRouter

from src.schemes.user import UserCreate, UserWithId
from src.services.user import UserService

router = APIRouter()


@router.get('/list')
async def get_users_list() -> list[UserWithId]:
    return UserService.get_users_list()


@router.post('/')
async def create_user(body: UserCreate) -> UserWithId:
    return UserService.create_user(body)
