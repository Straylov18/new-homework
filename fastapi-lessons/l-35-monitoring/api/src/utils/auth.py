from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from uuid import UUID

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Request
from pydantic import UUID4

from src.config import settings
from src.exception.common import ForbiddenException

password_hasher = PasswordHasher()


def get_password_hash(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Raises: ForbiddenException
    try:
        password_hasher.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False


def get_token(request: Request) -> str:
    # Raises: ForbiddenException
    token = request.cookies.get('access_token')
    if token is None:
        raise ForbiddenException('get system access', 'There is no jwt token')
    return token


def create_token(data: Dict[str, Any]) -> str:
    encode_jwt = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.TOKEN_ALGORITHM)
    return encode_jwt


def create_access_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire})
    return create_token(to_encode)


def get_token_payload_if_valid(token: str) -> Dict[str, Any]:
    # Raises: ForbiddenException
    try:
        payload: Dict[str, Any] = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.TOKEN_ALGORITHM)
    except jwt.InvalidTokenError:
        raise ForbiddenException('get system access', 'Failed to get valid jwt token!')

    expire: Optional[str] = payload.get('exp')
    if expire is None:
        raise ForbiddenException('get system access', 'Jwt token expired!')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if expire_time < datetime.now(timezone.utc):
        raise ForbiddenException('get system access', 'Jwt token expired!')

    return payload


def get_user_login_from_token(token: str) -> UUID4:
    # Raises: ForbiddenException
    jwt_payload = get_token_payload_if_valid(token)
    user_uid = jwt_payload.get('user_login')
    if not user_uid:
        raise ForbiddenException('get system access', 'There is no user_login in Jwt token!')
    return UUID(user_uid)
