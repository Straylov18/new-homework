from src.container.repository import repository_container
from src.scheme.task import TaskCreate, TaskInfo


class TaskService:

    @staticmethod
    async def create_task(data: TaskCreate) -> TaskInfo:
        new_task = await repository_container.task_repository().add_one(data.model_dump(exclude_unset=True))
        return new_task

    @staticmethod
    async def get_tasks_list() -> list[TaskInfo]:
        tasks = await repository_container.task_repository().get_list()
        return tasks
