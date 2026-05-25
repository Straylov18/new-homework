from datetime import date
from typing import Literal, Optional

from pydantic import UUID4, BaseModel, Field


class HelicopterRegistration(BaseModel):
    model_title: str = Field(
        description="Модель геликоптера"
    )


class DBHelicopter(BaseModel):
    uid: UUID4 = Field(
        description="UID геликоптера"
    )
    model_title: str = Field(
        description="Модель геликоптера"
    )
    registration_date: date = Field(
        description="Дата регистрации"
    )


class HelicopterFilter(BaseModel):
    # limit-offset
    limit: int = Field(
        description="Максимальное количество объектов в одной выдаче. Ограничение снимается, если лимит <= 0.",
        default=10
    )
    offset: int = Field(
        description="Для пропуска n объектов в выдаче.",
        default=0
    )
    # sort
    sort_by: Optional[Literal["model_title", "registration_date"]] = Field(
        description="Sort by column name.",
        default="registration_date"
    )
    sort_desc: bool = Field(
        description="Sort in descending or ascending order.",
        default=True
    )
    # str
    search_str: Optional[str] = Field(
        description="Поиск по текстовым полям хэликоптера.",
        default=None
    )
    # date
    registration_date_lte: Optional[date] = Field(
        description="Показывать только те геликоптэры, которые зарегистрированы до указанной даты (включительно).",
        default=None
    )
    registration_date_gte: Optional[date] = Field(
        description="Показывать только те геликоптэры, которые зарегистрированы после указанной даты (включительно).",
        default=None
    )
