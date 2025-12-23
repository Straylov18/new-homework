import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, UUID, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.adapter.db.session import Base
from src.scheme.user_post import UserPostFromDB


class UserPost(Base):
    __tablename__ = 'user_post'

    uid: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=True)
    date_created: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    user_uid: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("user.uid"), nullable=False)

    user = relationship("User", backref="user_posts")

    def serialize(self) -> UserPostFromDB:
        return UserPostFromDB(
            uid=self.uid,
            title=self.title,
            text=self.text,
            date_created=self.date_created,
            user_uid=self.user_uid,
        )
