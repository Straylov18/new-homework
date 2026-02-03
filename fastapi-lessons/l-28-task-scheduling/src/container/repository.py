from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.adapter.db.session import async_session_maker
from src.config import Settings, settings
from src.repository.task import TaskRepository


@dataclass
class RepositoryContainer:
    settings: Settings
    async_session_maker: async_sessionmaker[AsyncSession]

    def task_repository(self) -> TaskRepository:
        return TaskRepository(async_session_maker=self.async_session_maker)


repository_container = RepositoryContainer(settings=settings, async_session_maker=async_session_maker)
