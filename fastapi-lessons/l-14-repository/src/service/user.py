from fastapi import HTTPException, Response
from pydantic import EmailStr

from src.container.repository import repository_container
from src.model.user import User
from src.scheme.user import UserCreate, UserLogin
from src.utils.auth import (authenticate_user, create_access_token,
                            get_password_hash, get_token_payload_if_valid)


class UserService:

    @staticmethod
    async def create_user(data: UserCreate) -> User:
        user_with_same_email = await repository_container.user_repository().get_one(email=data.email)
        if user_with_same_email is not None:
            raise HTTPException(400, "такой пользователь уже есть")
        data.password = get_password_hash(data.password)
        data.is_admin = False
        new_user = await repository_container.user_repository().add_one(data.model_dump(exclude_unset=True))
        return new_user

    @staticmethod
    async def get_user_by_email(email: EmailStr) -> User:
        user = await repository_container.user_repository().get_one(email=email)
        if not user:
            raise HTTPException(status_code=404, detail="нету такого пользователя")
        return user

    @staticmethod
    async def get_users_list(token: str) -> list[User]:
        token_payload = get_token_payload_if_valid(token)
        user = await UserService.get_user_by_email(token_payload['email'])
        if not user.is_admin:
            raise HTTPException(403, "просматривать список пользователей может только админ!")
        users = await repository_container.user_repository().get_list()
        return users

    @staticmethod
    async def login(body: UserLogin, response: Response) -> str:
        await authenticate_user(body.email, body.password)  # will throw an exception on fail
        jwt_token_data = {"email": body.email}
        jwt_token = create_access_token(jwt_token_data)
        response.set_cookie("access_token", jwt_token)
        return "Успешный вход!"

    @staticmethod
    async def logout(response: Response) -> str:
        response.delete_cookie(key="access_token")
        return 'Пользователь вышел из системы. Бб, дружище!'
