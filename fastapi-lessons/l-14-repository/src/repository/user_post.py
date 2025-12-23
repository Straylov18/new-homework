from src.model.user_post import UserPost
from src.utils.repository import SQLAlchemyRepository


class UserPostRepository(SQLAlchemyRepository):
    model = UserPost
