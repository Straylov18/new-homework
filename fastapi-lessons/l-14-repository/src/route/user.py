from fastapi import APIRouter, Depends

from src.scheme.user import UserFromDB
from src.service.user import UserService
from src.utils.auth import get_token

router = APIRouter()


@router.get('/list')
async def get_users_list(token: str = Depends(get_token)) -> list[UserFromDB]:
    return [u.serialize() for u in await UserService.get_users_list(token)]
