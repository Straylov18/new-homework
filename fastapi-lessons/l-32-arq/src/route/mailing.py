"""
HTTP-эндпоинты рассылки писем.

Схемы (Pydantic-модели) вынесены в src.schema.mailing, здесь остаются
только обработчики запросов.
"""
from fastapi import APIRouter

from src.schema.mailing import MailAllResponse, MailRequest, TaskStatusResponse
from src.service.mailing import MailingService

router = APIRouter(prefix="/mailing")


@router.post("/send-to-all", response_model=MailAllResponse)
async def send_mail_to_all(payload: MailRequest) -> MailAllResponse:
    """
    Ставит в очередь задачу рассылки писем всем пользователям.

    Ответ возвращается сразу, без ожидания отправки писем:
    сама отправка выполняется в фоне ARQ worker-ом.
    """
    data = await MailingService.dispatch_mail_to_all(payload.subject, payload.body)
    return MailAllResponse(**data)


@router.get("/task/{task_id}", response_model=TaskStatusResponse)
async def task_status(task_id: str) -> TaskStatusResponse:
    """
    Показывает статус задачи по её идентификатору:
    DEFERRED / QUEUED / IN_PROGRESS / COMPLETE / NOT_FOUND.
    """
    data = await MailingService.get_task_status(task_id)
    return TaskStatusResponse(**data)
