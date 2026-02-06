from src.model.task import Task
from src.utils.repository import SQLAlchemyRepository


class TaskRepository(SQLAlchemyRepository):
    model = Task
