from fastapi import Response
from fastapi.routing import APIRouter

from src.config import settings
from src.exception.common import ForbiddenException
from src.metrics.business_logic import (user_logins_succeed_total,
                                        user_logins_total)
from src.schema.user import UserLogin
from src.utils.auth import create_access_token

router = APIRouter(prefix="/user")


@router.post('/login',
             response_model=str,
             responses={
                 403: {"description": "Incorrect login or password"}
             })
async def login(body: UserLogin, response: Response) -> str:
    # Добавляем счетчик логинов в систему
    user_logins_total.inc()

    if body.login != settings.ADMIN_LOGIN or body.password != settings.ADMIN_PASSWORD:
        raise ForbiddenException(reason="Incorrect login or password", action="login")
    jwt_token_data = {
        "user_login": str(settings.ADMIN_LOGIN),
    }
    jwt_token = create_access_token(jwt_token_data)
    response.set_cookie("access_token", jwt_token)
    user_logins_succeed_total.inc()
    return "Login succeeded"


@router.post("/logout")
async def logout(response: Response) -> str:
    response.delete_cookie(key="access_token")
    return "Logout succeeded"
