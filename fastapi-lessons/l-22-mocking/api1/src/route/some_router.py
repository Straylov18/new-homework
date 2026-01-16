from fastapi import APIRouter

from src.scheme.user import User
from src.service.some_service import get_successful_logins, login_user

router = APIRouter()


@router.post('/login')
async def login(body: User):
    return login_user(body)


@router.get('/list-successful-logins')
async def get_logins_info() -> list[User]:
    return get_successful_logins()
