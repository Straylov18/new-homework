import logging
from contextlib import asynccontextmanager

import uvicorn
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI
from fastapi.routing import APIRouter

from src.config import settings
from src.container.scheduler import SchedulerContainer
from src.route.scheduler_job import router as task_scheduler_router
from src.route.task import router as task_router
from src.scheduler.task_scheduler import schedule_task

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        default_scheduler_id = 'default_create_task_job'
        SchedulerContainer.get_scheduler().add_job(
            schedule_task,
            trigger=IntervalTrigger(seconds=settings.DEFAULT_SCHEDULING_PERIOD),
            id=default_scheduler_id,
            replace_existing=True,
            kwargs={'scheduler_id': default_scheduler_id}
        )
        SchedulerContainer.get_scheduler().start()
        logger.info('Task scheduler started')
        yield
    except Exception as e:
        logger.error(f'Task scheduler default job initialization errors: {e}')
    finally:
        SchedulerContainer.get_scheduler().shutdown()
        # SchedulerContainer.get_scheduler().shutdown(wait=True)
        logger.info('Task scheduler job stopped')


app = FastAPI(
    openapi_url=f'{settings.BASE_ROUTE_PATH}/openapi.json',
    docs_url=f'{settings.BASE_ROUTE_PATH}/docs',
    lifespan=lifespan,
)

router = APIRouter(prefix=settings.BASE_ROUTE_PATH)

router.include_router(task_router, prefix='/task', tags=['task'])
router.include_router(task_scheduler_router, prefix='/task_scheduler', tags=['task_scheduler'])

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
