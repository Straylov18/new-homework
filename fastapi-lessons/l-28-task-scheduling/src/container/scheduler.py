from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class SchedulerContainer:
    scheduler: AsyncIOScheduler = None

    @classmethod
    def get_scheduler(cls) -> AsyncIOScheduler:
        if cls.scheduler is None:
            jobstores = {
                'default': RedisJobStore(jobs_key='dispatched_trips_jobs', run_times_key='dispatched_trips_running',
                                         host='localhost', port=6380)
            }
            cls.scheduler = AsyncIOScheduler(jobstores=jobstores)
            # cls.scheduler = AsyncIOScheduler()

        return cls.scheduler
