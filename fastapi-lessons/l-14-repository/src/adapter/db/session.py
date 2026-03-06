from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

if settings.DB.SQLALCHEMY_DATABASE_URI_ASYNC is None:
    raise Exception('Failed to get SQLALCHEMY_DATABASE_URI_ASYNC')
engine: AsyncEngine = create_async_engine(url=settings.DB.SQLALCHEMY_DATABASE_URI_ASYNC)
async_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass