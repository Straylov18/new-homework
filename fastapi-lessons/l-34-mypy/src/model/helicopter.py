import uuid
from datetime import date

from sqlalchemy import UUID, Date, String
from sqlalchemy.orm import Mapped, mapped_column

from src.adapter.db.session import Base


class HelicopterModel(Base):
    __tablename__ = 'helicopter'

    uid: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4
    )
    login: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    registration_date: Mapped[date] = mapped_column(
        Date,
        default=date.today()
    )
