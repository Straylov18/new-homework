import uuid
from datetime import date

from sqlalchemy import UUID, Date, String
from sqlalchemy.orm import Mapped, mapped_column

from src.adapter.db.session import Base
from src.schema.outputs import HelicopterOutput


class HelicopterModel(Base):
    __tablename__ = 'helicopter'

    uid: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4
    )
    model_title: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    registration_date: Mapped[date] = mapped_column(
        Date,
        default=date.today()
    )

    def get_output_schema(self) -> HelicopterOutput:
        return HelicopterOutput(**self.__dict__)
