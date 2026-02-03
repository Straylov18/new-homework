import logging

from src.container.scheduler import SchedulerContainer
from src.scheme.task import TaskCreate
from src.service.task import TaskService

logger = logging.getLogger(__name__)

scheduler = SchedulerContainer.get_scheduler()


async def schedule_task(scheduler_id: str):
    task_info = TaskCreate(
        description=f'task created by scheduler with id {scheduler_id}',
        scheduler_id=scheduler_id
    )
    await TaskService.create_task(task_info)
    logger.info(f'Task created by scheduler {scheduler_id}')


@scheduler.scheduled_job('interval', id='warning_job_from_decorator_id', seconds=2)
async def job_from_decorator():
    logger.warning('called from func scheduled with decorator')
