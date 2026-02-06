from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.config import settings


class SchedulerContainer:
    scheduler: AsyncIOScheduler = None

    @classmethod
    def get_scheduler(cls) -> AsyncIOScheduler:
        if cls.scheduler is None:
            jobstores = {
                'default': RedisJobStore(
                    jobs_key='dispatched_tasks_jobs',
                    run_times_key='dispatched_tasks_running',
                    host=settings.REDIS.REDIS_SERVER,
                    port=settings.REDIS.REDIS_PORT,
                    db=settings.REDIS.REDIS_DB,
                    username=settings.REDIS.REDIS_USER,
                    password=settings.REDIS.REDIS_PASSWORD,
                )
            }
            # cls.scheduler = AsyncIOScheduler()
            cls.scheduler = AsyncIOScheduler(jobstores=jobstores)

        return cls.scheduler
