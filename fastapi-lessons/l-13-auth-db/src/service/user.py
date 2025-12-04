from fastapi import HTTPException, Response
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.user import User
from src.scheme.user import UserCreate, UserLogin
from src.utils.auth import (authenticate_user, create_access_token,
                            get_password_hash, get_token_payload_if_valid)


class UserService:

    @staticmethod
    async def create_user(data: UserCreate, db_session: AsyncSession) -> User:
        if await UserService.is_user_already_exists(data.email, db_session):
            raise HTTPException(400, "такой пользователь уже есть")
        new_user = User(**data.model_dump(exclude_unset=True))
        new_user.password = get_password_hash(new_user.password)
        new_user.is_admin = False
        db_session.add(new_user)
        await db_session.commit()
        await db_session.refresh(new_user)
        return new_user

    @staticmethod
    async def is_user_already_exists(email: EmailStr, db_session: AsyncSession) -> bool:
        query = await db_session.execute(select(User).where(User.email == email))
        user = query.scalar_one_or_none()
        if not user:
            return False
        return True

    @staticmethod
    async def get_user_by_email(email: EmailStr, db_session: AsyncSession) -> User:
        query = await db_session.execute(select(User).where(User.email == email))
        user = query.scalar_one_or_none()
        if not user:
            raise HTTPException(404, "нету такого пользователя")
        return user

    @staticmethod
    async def get_users_list(token: str, db_session: AsyncSession) -> list[User]:
        token_payload = get_token_payload_if_valid(token)
        user = await UserService.get_user_by_email(token_payload['email'], db_session)
        if not user.is_admin:
            raise HTTPException(403, "просматривать список пользователей может только админ!")
        query_result = await db_session.execute(select(User))
        return query_result.scalars().all()

    @staticmethod
    async def login(body: UserLogin, response: Response, db_session: AsyncSession) -> str:
        await authenticate_user(body.email, body.password, db_session)  # will throw an exception on fail
        jwt_token_data = {"email": body.email}
        jwt_token = create_access_token(jwt_token_data)
        response.set_cookie("access_token", jwt_token)
        return "Успешный вход!"

    @staticmethod
    async def logout(response: Response) -> str:
        response.delete_cookie(key="access_token")
        return 'Пользователь вышел из системы. Бб, дружище!'
