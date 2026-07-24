import json
from functools import partial
from typing import Final

from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

# Custom serializer with ensure_ascii=False
utf8_serializer = partial(json.dumps, ensure_ascii=False)

if settings.DB.SQLALCHEMY_DATABASE_URI_ASYNC is None:
    raise Exception('Failed to get SQLALCHEMY_DATABASE_URI_ASYNC')

engine: Final[AsyncEngine] = create_async_engine(
    url=settings.DB.SQLALCHEMY_DATABASE_URI_ASYNC,
    echo=settings.DB.POSTGRES_DB_ECHO,
    json_serializer=utf8_serializer
)
async_session_maker: Final[async_sessionmaker[AsyncSession]] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
