from pydantic import UUID4, BaseModel, Field


class UserPostCreate(BaseModel):
    title: str | None = Field(description="Post title", default="Post title")
    text: str | None = Field(description="Post text", default=None)
    user_uid: UUID4 = Field(description="User uid")


class UserPostFromDB(BaseModel):
    uid: UUID4 = Field(description="User post uid")
    title: str | None = Field(description="Post title", default="Post title")
    text: str | None = Field(description="Post text", default=None)
    user_uid: UUID4 = Field(description="User uid")
