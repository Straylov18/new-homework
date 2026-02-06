from pydantic import BaseModel, Field


class SchedulerJob(BaseModel):
    id: str = Field(description="Scheduler id")
    period: int | None = Field(description="Period", default=1)
