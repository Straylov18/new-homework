from datetime import date

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
