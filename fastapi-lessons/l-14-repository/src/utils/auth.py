from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import HTTPException, Request
from pydantic import EmailStr

from src.config import settings
from src.container.repository import repository_container
from src.model.user import User

password_hasher = PasswordHasher()


def get_password_hash(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        password_hasher.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False


async def authenticate_user(email: EmailStr, password: str) -> User:
    user = await repository_container.user_repository().get_one(email=email)
    if not user:
        raise HTTPException(404, "Нету такого пользователя!")
    if not user or verify_password(plain_password=password, hashed_password=user.password) is False:
        raise HTTPException(404, "А-а! Неверный пароль!")
    return user


def get_token(request: Request):
    token = request.cookies.get('access_token')
    if not token:
        raise HTTPException(403, "нету токена")
    return token


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm='HS256')
    return encode_jwt


def get_token_payload_if_valid(token) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
    except jwt.InvalidTokenError:
        raise HTTPException(403, "Нет валидного jwt токена!")

    expire: str = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        raise HTTPException(403, "jwt токен просрочился")

    return payload
