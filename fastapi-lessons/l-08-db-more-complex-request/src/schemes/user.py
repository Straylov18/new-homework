from pydantic import BaseModel, Field, ConfigDict, UUID4


class UserCreate(BaseModel):
    name: str | None = Field(description="Name", default=None)
    email: str | None = Field(description="Email", default=None)


class UserFromDB(BaseModel):
    id: int | None = Field(description="User id")
    # uid: UUID4 = Field(description="User uid")
    name: str | None = Field(description="Name", default=None)
    email: str | None = Field(description="Email", default=None)

class Filters(BaseModel):
    search_str: str | None = Field(description="Search by text in user parameters", default=None)
    # date_from
    # date_to
    # emails_list
