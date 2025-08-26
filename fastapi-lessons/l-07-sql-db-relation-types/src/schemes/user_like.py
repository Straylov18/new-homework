from pydantic import BaseModel, Field, UUID4


class UserLikeCreate(BaseModel):
    user_uid: UUID4 = Field(description="User uid")
    user_post_uid: UUID4 = Field(description="User post uid")


class UserLikeFromDB(BaseModel):
    uid: UUID4 = Field(description="User like uid")
    user_uid: UUID4 = Field(description="User uid")
    user_post_uid: UUID4 = Field(description="User post uid")
