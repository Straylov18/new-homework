from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one():
        raise NotImplementedError

    @abstractmethod
    async def get_one():
        raise NotImplementedError

    @abstractmethod
    async def get_list():
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None

    def __init__(self, async_session_maker: AsyncSession):
        self.async_session_maker = async_session_maker

    async def add_one(self, data: dict):
        obj = self.model(**data)
        async with self.async_session_maker() as session:
            session.add(obj)
            await session.commit()
        return obj

    async def get_one(self, **filter_by):
        async with self.async_session_maker() as session:
            query = select(self.model).filter_by(**filter_by)
            res = await session.execute(query)
            res = res.scalar_one_or_none()
        return res

    async def get_list(self, **filter_by):
        async with self.async_session_maker() as session:
            query = select(self.model)
            res = await session.execute(query)
            res = [row[0] for row in res.all()]
        return res
