import uuid

from sqlalchemy import UUID, Boolean, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.adapter.db.session import Base
from src.scheme.user import UserFromDB


class User(Base):
    __tablename__ = 'user'
    __table_args__ = (UniqueConstraint('email', name='_user_email'),)

    uid: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def serialize(self) -> UserFromDB:
        return UserFromDB(
            uid=self.uid,
            name=self.name,
            email=self.email,
            is_admin=self.is_admin,
        )
