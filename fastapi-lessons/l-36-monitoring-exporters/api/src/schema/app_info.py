from pydantic import BaseModel, Field


class AppInfo(BaseModel):
    back_version: str = Field(
        description="Версия серверной части приложения"
    )
