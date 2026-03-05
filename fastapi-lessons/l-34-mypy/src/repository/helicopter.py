from typing import Any, Dict, Sequence

from pydantic import UUID4

from src.model.helicopter import HelicopterModel
from src.utils.repository import SQLAlchemyRepository


class HelicopterRepository(SQLAlchemyRepository):
    _model = HelicopterModel

    async def add_one(self, data: Dict[str, Any]) -> HelicopterModel:
        return await super().add_one(data)

    async def get_one(self, **filter_by: Any) -> HelicopterModel:
        return await super().get_one(**filter_by)

    async def get_list(self, limit: int, offset: int, **filter_by: Any) -> Sequence[HelicopterModel]:
        return await super().get_list(limit, offset, **filter_by)

    async def delete_one(self, **filter_by: Any) -> HelicopterModel:
        return await super().delete_one(**filter_by)

    async def update_one(self, uid: UUID4, update_data: Dict[str, Any]) -> HelicopterModel:
        return await super().update_one(uid, update_data)
