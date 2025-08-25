from pydantic import BaseModel, Field, ConfigDict, UUID4

from src.schemes.user import UserFromDB


class UserPostCreate(BaseModel):
    title: str | None = Field(description="Post title", default="Post title")
    text: str | None = Field(description="Post text", default=None)
    user_uid: UUID4 = Field(description="User uid")


class UserPostFromDB(BaseModel):
    uid: UUID4 = Field(description="User post uid")
    title: str | None = Field(description="Post title", default="Post title")
    text: str | None = Field(description="Post text", default=None)
    user_uid: UUID4 = Field(description="User uid")


class UserPostFull(BaseModel):
    uid: UUID4 = Field(description="User post uid")
    title: str | None = Field(description="Post title", default="Post title")
    text: str | None = Field(description="Post text", default=None)
    user: UserFromDB = Field(description="User")
