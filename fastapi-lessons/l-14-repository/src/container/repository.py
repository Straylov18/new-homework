from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.adapter.db.session import async_session_maker
from src.config import Settings, settings
from src.repository.user import UserRepository
from src.repository.user_post import UserPostRepository


@dataclass
class RepositoryContainer:
    settings: Settings
    async_session_maker: async_sessionmaker[AsyncSession]

    def user_repository(self) -> UserRepository:
        return UserRepository(async_session_maker=self.async_session_maker)

    def user_post_repository(self) -> UserPostRepository:
        return UserPostRepository(async_session_maker=self.async_session_maker)


repository_container = RepositoryContainer(settings=settings, async_session_maker=async_session_maker)
