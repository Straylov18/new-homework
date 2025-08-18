from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
from src.config import settings

# database_url = 'sqlite+aiosqlite:///db.sqlite3'
engine = create_async_engine(url=settings.SQLALCHEMY_DATABASE_URL)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)
Base = declarative_base()
