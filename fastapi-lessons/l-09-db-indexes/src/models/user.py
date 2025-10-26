import uuid

from sqlalchemy import UUID, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.session import Base
from src.schemes.user import UserFromDB


class User(Base):
    __tablename__ = 'user'

    uid: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)

    def serialize(self) -> UserFromDB:
        return UserFromDB(
            uid=self.uid,
            name=self.name,
            email=self.email,
        )
