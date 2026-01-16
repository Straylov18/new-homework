from pydantic import BaseModel, Field


class User(BaseModel):
    email: str | None = Field(description="Email", default=None)
    password: str | None = Field(description="Password", default=None)
