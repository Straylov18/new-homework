from typing import List

from pydantic import BaseModel, Field

from src.schema.app_info import AppInfo
from src.schema.helicopter import DBHelicopter


class AppInfoOutput(AppInfo):
    pass


class HelicopterOutput(DBHelicopter):
    pass


class HelicopterListedOutput(BaseModel):
    items: List[HelicopterOutput]
    count: int = Field(
        description="Суммарное количество отфильтрованных записей без учета пагинации."
    )
