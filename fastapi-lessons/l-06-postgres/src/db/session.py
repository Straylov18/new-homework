from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.config import settings

engine = create_async_engine(url=settings.DB.SQLALCHEMY_DATABASE_URI)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)
Base = declarative_base()

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
