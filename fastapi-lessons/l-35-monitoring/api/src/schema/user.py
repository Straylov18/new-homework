from pydantic import BaseModel, Field


class UserLogin(BaseModel):
    # str
    login: str = Field(
        description="Login"
    )
    password: str = Field(
        description="Password"
    )
