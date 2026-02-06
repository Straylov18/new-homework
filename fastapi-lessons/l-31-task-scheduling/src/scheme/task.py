from datetime import datetime

from pydantic import UUID4, BaseModel, Field


class TaskCreate(BaseModel):
    description: str | None = Field(description="Task description", default=None)
    scheduler_id: str = Field(description="Scheduler id")


class TaskInfo(BaseModel):
    uid: UUID4 = Field(description="Task uid")
    description: str | None = Field(description="Task description", default=None)
    date_created: datetime = Field(description="The date when task was created")
    scheduler_id: str = Field(description="Scheduler id")
