import logging

from fastapi import APIRouter

from src.scheme.scheduler_job import SchedulerJob
from src.service.scheduler_job import SchedulerJobService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get('/list')
async def get_task_scheduler_jobs_list() -> list[SchedulerJob]:
    return await SchedulerJobService.get_task_scheduler_jobs_list()


@router.post('/')
async def create_task_scheduler_job(data: SchedulerJob) -> SchedulerJob:
    task_scheduler = await SchedulerJobService.create_task_scheduler_job(data)
    logger.info(f'Created new scheduler {task_scheduler}')
    return task_scheduler


@router.delete('/{scheduler_id}')
async def remove_task_scheduler_job(scheduler_id: str):
    await SchedulerJobService.remove_task_scheduler_job(scheduler_id)
    logger.info(f'Scheduler with id {scheduler_id} was removed')
    return 'scheduler removed'
