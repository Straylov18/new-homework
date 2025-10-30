from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, UUID4


class UserCreate(BaseModel):
    name: str | None = Field(description="Name", default=None)
    email: str | None = Field(description="Email", default=None)


class UserFromDB(BaseModel):
    uid: UUID4 | None = Field(description="User id")
    name: str | None = Field(description="Name", default=None)
    email: str | None = Field(description="Email", default=None)
    date_created: datetime | None = Field(description="Date when user was created", default=None)


class Filters(BaseModel):
    search_str: str | None = Field(description="Search by text in user parameters", default=None)
    limit: int | None = Field(description="Limit", default=10)
    offset: int | None = Field(description="Offset", default=0)
    order_by: str | None = Field(description="Order by", default="name")
    order_desc: bool | None = Field(description="Order in descending order", default=True)
    date_created__gte: datetime | None = Field(description="Show only users created after date", default=None)
    date_created__lte: datetime | None = Field(description="Show only users created before date", default=None)
    email__in: list[str] | None = Field(description="Email in list", default=None)
