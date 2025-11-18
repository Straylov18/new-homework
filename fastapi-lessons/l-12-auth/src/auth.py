# from passlib.context import CryptContext
# from pydantic import EmailStr
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Request, HTTPException

from src.config import settings


# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#
#
# def get_password_hash(password: str) -> str:
#     return pwd_context.hash(password)
#
#
# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)
#
#
# def authenticate_user(email: EmailStr, password: str):
#     user = {"hashed_password": "123"}  # TODO get by email
#     if not user or verify_password(plain_password=password, hashed_password=user.hashed_password) is False:
#         return None
#     return user


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
