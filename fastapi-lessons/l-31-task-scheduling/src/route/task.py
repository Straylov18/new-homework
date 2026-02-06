from fastapi import APIRouter

from src.scheme.task import TaskInfo
from src.service.task import TaskService

router = APIRouter()


@router.get('/list')
async def get_tasks_list() -> list[TaskInfo]:
    return await TaskService.get_tasks_list()
