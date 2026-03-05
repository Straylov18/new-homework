from abc import ABC, abstractmethod
from typing import Any, Dict, Sequence

from pydantic import UUID4
from sqlalchemy import Select, select

from src.adapter.db.session import Base, async_session_maker


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: Dict[str, Any]) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def get_one(self, **filter_by: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def get_list(self, limit: int, offset: int, **filter_by: Any) -> Sequence[Any]:
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, **filter_by: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def update_one(self, uid: UUID4, update_data: Dict[str, Any]) -> Any:
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    _model: Base

    @property
    def model(self) -> Base:
        return self._model

    def __init__(self) -> None:
        self.session = async_session_maker

    def _get_filtered_query(self, query: Select[Base],
                            filter_attributes: Dict[str, Any]) -> Select[Base]:
        return query

    async def fetch_one(self, query: Select[Base]) -> Any:
        async with self.session() as session:
            res = await session.execute(query)
            return res.scalar_one_or_none()

    async def fetch_all(self, query: Select[Base]) -> Sequence[Any]:
        async with self.session() as session:
            res = await session.execute(query)
            return res.scalars().unique().all()

    async def add_one(self, data: Dict[str, Any]) -> Any:
        obj = self.model(**data)
        async with self.session() as session:
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    async def get_one(self, **filter_by: Any) -> Any:
        query = select(self.model).filter_by(**filter_by)
        return await self.fetch_one(query)

    async def get_list(self, limit: int, offset: int, **filter_by: Any) -> Sequence[Any]:
        query = select(self.model)
        query = self._get_filtered_query(query, filter_by)
        if limit > 0:
            query = query.limit(limit)
        query = query.offset(offset)
        return await self.fetch_all(query)

    async def delete_one(self, **filter_by: Any) -> Any:
        async with self.session() as session:
            query = select(self.model).filter_by(**filter_by)
            res = await session.execute(query)
            obj = res.scalar_one_or_none()
            if obj:
                await session.delete(obj)
            await session.commit()
            return obj

    async def update_one(self, uid: UUID4, update_data: Dict[str, Any]) -> Any:
        async with self.session() as session:
            query = select(self.model).filter_by(uid=uid)
            res = await session.execute(query)
            obj = res.scalar_one_or_none()
            if obj:
                for key, value in update_data.items():
                    setattr(obj, key, value)
                session.add(obj)
                await session.commit()
                await session.refresh(obj)
            return obj
