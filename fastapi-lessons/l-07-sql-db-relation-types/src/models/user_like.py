import uuid

from sqlalchemy import UUID, ForeignKey, String, TIMESTAMP, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.session import Base
from src.schemes.user_like import UserLikeFromDB


class UserLike(Base):
    __tablename__ = 'user_like'
    __table_args__ = (UniqueConstraint('user_uid', 'user_post_uid', name='_user_post_to_user'),)

    uid: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)

    user_uid: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("user.uid"), nullable=False)
    user_post_uid: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("user_post.uid"), nullable=False)

    user = relationship("User", backref="user_likes")
    user_post = relationship("UserPost", backref="user_post_likes")

    def serialize(self) -> UserLikeFromDB:
        return UserLikeFromDB(
            uid=self.uid,
            user_uid=self.user_uid,
            user_post_uid=self.user_post_uid,
        )
