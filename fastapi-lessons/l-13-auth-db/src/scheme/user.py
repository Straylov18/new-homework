from pydantic import UUID4, BaseModel, Field


class UserCreate(BaseModel):
    name: str | None = Field(description="Name", default=None)
    email: str | None = Field(description="Email", default=None)
    password: str | None = Field(description="Password", default=None)


class UserLogin(BaseModel):
    email: str | None = Field(description="Email", default=None)
    password: str | None = Field(description="Password", default=None)


class UserFromDB(BaseModel):
    uid: UUID4 = Field(description="User uid")
    name: str | None = Field(description="Name", default=None)
    email: str | None = Field(description="Email", default=None)
    is_admin: bool = Field(description="Is this user admin or not", default=False)
