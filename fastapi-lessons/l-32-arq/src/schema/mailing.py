"""
Pydantic-схемы (слой схем) для рассылки писем.

Сюда вынесены все DTO/схемы, которые раньше жили прямо в роуте.
Роуты теперь только описывают HTTP-обработчики и опираются на эти схемы.
"""
from typing import Any

from pydantic import BaseModel, Field


class MailRequest(BaseModel):
    subject: str = Field(default="Hello from FastAPI + ARQ")
    body: str = Field(default="This is a test mailing.")


class MailAllResponse(BaseModel):
    task_id: str
    recipients_count: int
    recipients: list[str]
    status: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    successful: bool
    result: Any | None
