from pydantic import BaseModel, Field, ConfigDict, UUID4


class UserCreate(BaseModel):
    name: str | None = Field(description="Name", default=None)
    email: str | None = Field(description="Email", default=None)


class UserFromDB(BaseModel):
    uid: UUID4 = Field(description="User uid")
    name: str | None = Field(description="Name", default=None)
    email: str | None = Field(description="Email", default=None)
