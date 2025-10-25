import uuid
from sqlalchemy import UUID
from datetime import datetime
from sqlalchemy import String, Integer, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from src.db.session import Base


class User(Base):
    __tablename__ = 'users'

    uid: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    date_created: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
