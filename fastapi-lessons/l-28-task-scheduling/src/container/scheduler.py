from apscheduler.schedulers.asyncio import AsyncIOScheduler


class SchedulerContainer:
    scheduler: AsyncIOScheduler = None

    @classmethod
    def get_scheduler(cls) -> AsyncIOScheduler:
        if cls.scheduler is None:
            cls.scheduler = AsyncIOScheduler()
        return cls.scheduler
