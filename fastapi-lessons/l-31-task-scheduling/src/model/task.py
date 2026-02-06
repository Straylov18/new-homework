import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, UUID, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.adapter.db.session import Base


class Task(Base):
    __tablename__ = 'task'

    uid: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    description: Mapped[str] = mapped_column(String, nullable=False)
    date_created: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    scheduler_id: Mapped[str] = mapped_column(String, nullable=False)
