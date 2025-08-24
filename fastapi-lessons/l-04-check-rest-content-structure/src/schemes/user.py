from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    name: str | None = Field(description="Name", default=None)
    email: str | None = Field(description="Email", default=None)


class UserWithId(BaseModel):
    id: int | None = Field(description="User id", gt=-1)  # gt=-1 означает, что поле id должно быть > -1
    name: str | None = Field(description="Name", default=None)
    email: str | None = Field(description="Email", default=None)
