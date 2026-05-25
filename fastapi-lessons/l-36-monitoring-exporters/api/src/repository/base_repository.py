from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Sequence, Type, TypeVar

from pydantic import UUID4
from sqlalchemy import Select, func, select
from sqlalchemy.sql.expression import desc

from src.adapter.db.session import Base, async_session_maker
from src.exception.common import NotFoundException

T = TypeVar("T", bound=Base)


class AbstractRepository(Generic[T], ABC):
    @abstractmethod
    async def add_one(self, data: Dict[str, Any]) -> T:
        raise NotImplementedError

    @abstractmethod
    async def add_bulk(self, data: List[Dict[str, Any]]) -> List[T]:
        raise NotImplementedError

    @abstractmethod
    async def get_one(self, **filter_by: Any) -> T | None:
        raise NotImplementedError

    @abstractmethod
    async def get_list(self, limit: int, offset: int, **filter_by: Any) -> Sequence[T]:
        raise NotImplementedError

    @abstractmethod
    async def get_count(self, **filter_by: Any) -> int:
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, **filter_by: Any) -> T:
        raise NotImplementedError

    @abstractmethod
    async def update_one(self, uid: UUID4, update_data: Dict[str, Any]) -> T:
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository[T]):
    _model: Type[T]

    @property
    def model(self) -> Type[T]:
        return self._model

    def __init__(self) -> None:
        self.session = async_session_maker

    def _get_filtered_query(self, query: Select[tuple[Any]],
                            filter_attributes: Dict[str, Any]) -> Select[tuple[Any]]:
        return query

    def _apply_limit_offset_to_query(self, query: Select[tuple[Any]],
                                     limit: int = 10, offset: int = 0) -> Select[tuple[Any]]:
        if limit > 0:
            query = query.limit(limit)
        query = query.offset(offset)
        return query

    def _apply_sort_to_query(self, query: Select[tuple[Any]],
                             sort_by: str = 'uid', sort_desc: bool = True) -> Select[tuple[Any]]:
        if sort_desc:
            return query.order_by(desc(getattr(self.model, sort_by)))
        else:
            return query.order_by(getattr(self.model, sort_by))

    async def _fetch_one(self, query: Select[tuple[T]]) -> T:
        # Raises: NotFoundException if there is no filtered objects
        async with self.session() as session:
            res = await session.execute(query)
            output = res.unique().scalar_one_or_none()
            if output is None:
                raise NotFoundException(resource=self.model.__tablename__)
            return output

    async def _fetch_all(self, query: Select[tuple[T]]) -> Sequence[T]:
        async with self.session() as session:
            res = await session.execute(query)
            return res.scalars().unique().all()

    async def add_one(self, data: Dict[str, Any]) -> T:
        obj = self.model(**data)
        async with self.session() as session:
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    async def add_bulk(self, data: List[Dict[str, Any]]) -> List[T]:
        output = []
        async with self.session() as session:
            for d in data:
                obj = self.model(**d)
                output.append(obj)
                session.add(obj)
            await session.commit()
            for o in output:
                await session.refresh(o)
        return output

    async def get_one(self, **filter_by: Any) -> T:
        # Raises: NotFoundException if there is no filtered objects
        query = select(self.model).filter_by(**filter_by)
        return await self._fetch_one(query)

    async def get_list(self, limit: int = 10, offset: int = 0,
                       sort_by: str = 'uid', sort_desc: bool = True,
                       **filter_by: Any) -> Sequence[T]:
        query = select(self.model)
        query = self._get_filtered_query(query, filter_by)

        query = self._apply_limit_offset_to_query(query, limit, offset)
        query = self._apply_sort_to_query(query, sort_by, sort_desc)
        return await self._fetch_all(query)

    async def get_count(self, **filter_by: Any) -> int:
        query = select(func.count()).select_from(self.model)
        query = self._get_filtered_query(query, filter_by)
        async with self.session() as session:
            res = await session.execute(query)
            return res.scalar_one()

    async def delete_one(self, **filter_by: Any) -> T:
        # Raises: NotFoundException if there is no filtered objects
        async with self.session() as session:
            query = select(self.model).filter_by(**filter_by)
            res = await session.execute(query)
            obj = res.scalar_one_or_none()
            if obj is None:
                raise NotFoundException(resource=self.model.__tablename__, filter=filter_by)
            if obj:
                await session.delete(obj)
            await session.commit()
            return obj

    async def update_one(self, uid: UUID4, update_data: Dict[str, Any]) -> T:
        # Raises: NotFoundException if there is no filtered objects
        async with self.session() as session:
            query = select(self.model).filter_by(uid=uid)
            res = await session.execute(query)
            obj = res.scalar_one_or_none()
            if obj is None:
                raise NotFoundException(resource=self.model.__tablename__, filter={'uid': uid})
            for key, value in update_data.items():
                setattr(obj, key, value)
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj
