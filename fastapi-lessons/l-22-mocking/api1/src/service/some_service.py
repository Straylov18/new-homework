import httpx
from fastapi import HTTPException

from src.config import settings
from src.scheme.user import User

successful_logins: list[User] = []


def try_login_in_auth_server(user: User) -> bool:
    r = httpx.post(f'{settings.AUTH_SERVER_ADDRESS}/user/login', json=user.model_dump())
    if r.json() == 'login succeeded':
        return True
    return False


def login_user(user: User):
    if try_login_in_auth_server(user):
        successful_logins.append(user)
        return 'Залогинились через отдельностоящий сервис'
    else:
        raise HTTPException(status_code=400, detail="Не получилось войти через отдельностоящий сервис!")


def get_successful_logins() -> list[User]:
    return successful_logins
