from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.config import settings

# database_url = 'sqlite+aiosqlite:///db.sqlite3'
engine = create_async_engine(url=settings.SQLALCHEMY_DATABASE_URL)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)
Base = declarative_base()

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
