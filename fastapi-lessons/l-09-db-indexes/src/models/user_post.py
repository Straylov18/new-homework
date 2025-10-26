import uuid
from datetime import datetime

from sqlalchemy import UUID, ForeignKey, String, Integer, TIMESTAMP, func, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.session import Base
from src.schemes.user_post import UserPostFromDB


class UserPost(Base):
    __tablename__ = 'user_post'
    __table_args__ = (
        Index('title_index', 'title'),
        Index('date_created_user_uid_index', 'date_created', 'user_uid'),
        CheckConstraint('number_of_updates > 0', 'number_of_updates should pe more than 0')
    )

    uid: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=True)
    number_of_updates: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
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
