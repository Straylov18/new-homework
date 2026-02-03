from apscheduler.triggers.interval import IntervalTrigger

from src.container.scheduler import SchedulerContainer
from src.scheduler.task_scheduler import schedule_task
from src.scheme.scheduler_job import SchedulerJob


class SchedulerJobService:

    @staticmethod
    async def create_task_scheduler_job(data: SchedulerJob) -> SchedulerJob:
        current_scheduler_id = data.id
        scheduler = SchedulerContainer.get_scheduler()
        scheduler.add_job(
            schedule_task,
            trigger=IntervalTrigger(seconds=data.period),
            id=current_scheduler_id,
            replace_existing=True,
            kwargs={'scheduler_id': current_scheduler_id}
        )
        return scheduler.get_job(current_scheduler_id)

    @staticmethod
    async def get_task_scheduler_jobs_list() -> list[SchedulerJob]:
        output = []
        for j in SchedulerContainer.get_scheduler().get_jobs():
            interval_str = str(j.trigger.interval)
            i_split = [int(i) for i in interval_str.split(':')]
            output.append(SchedulerJob(
                id=j.id,
                period=i_split[2] + 60 * i_split[1] + 3600 * i_split[0]
            ))
        return output

    @staticmethod
    async def remove_task_scheduler_job(scheduler_job_id):
        SchedulerContainer.get_scheduler().remove_job(scheduler_job_id)
