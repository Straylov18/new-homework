from fastapi import APIRouter

from src.schemes.user import UserCreate, UserFromDB

router = APIRouter()


@router.get('/list')
async def get_users_list() -> list[UserCreate]:
    pass
    # return users


@router.post('/')
async def create_user(body: UserCreate) -> UserFromDB:
    pass
    # return users
