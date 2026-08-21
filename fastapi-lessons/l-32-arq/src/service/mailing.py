from typing import Any

from arq import create_pool
from arq.jobs import Job, JobStatus

from src.config import settings


class MailingService:
    @staticmethod
    async def get_recipients() -> list[str]:
        return list([f'user{i}@example.com' for i in range(100)])  # TODO вынести

    @staticmethod
    async def dispatch_mail_to_all(subject: str, body: str) -> dict[str, Any]:
        """
        Ставит в очередь задачу рассылки писем всем пользователям.

        :param subject: тема письма
        :param body:    текст письма
        :return:        идентификатор поставленной задачи + инфо о получателях
        """
        recipients = await MailingService.get_recipients()

        # Создаём пул соединений с Redis (очередь ARQ).
        redis = await create_pool(
            settings.arq_redis_settings,
            default_queue_name=settings.ARQ.ARQ_QUEUE_NAME,
        )
        try:
            # enqueue_job кладёт задачу в очередь: worker подхватит её
            # и выполнит в фоне. Метод возвращает объект Job с job_id.
            # Срок хранения результата задаётся в настройках worker (keep_result).
            job = await redis.enqueue_job(
                'send_many_emails',  # функции, которые можно дергать заданы в functions в arq_app.py
                recipients,
                subject,
                body,
                _queue_name=settings.ARQ.ARQ_QUEUE_NAME,
            )
        finally:
            await redis.close()

        # Сразу после постановки задача ещё может не начать выполняться.
        job_info = await MailingService._read_job(job.job_id)

        return {
            'task_id': job.job_id,
            'recipients_count': len(recipients),
            'recipients': recipients,
            'status': job_info['status'],
        }

    @staticmethod
    async def get_task_status(task_id: str) -> dict[str, Any]:
        """
        Возвращает статус задачи по её идентификатору.

        ARQ хранит статус и результат каждой задачи в Redis, поэтому их можно
        прочитать из любого процесса, у которого есть job_id.
        """
        return await MailingService._read_job(task_id)

    @staticmethod
    async def _read_job(job_id: str) -> dict[str, Any]:
        """
        Читает статус и результат задачи из Redis.

        Объект Job создаётся напрямую по job_id. `await job.status()` возвращает
        JobStatus (deferred / queued / in_progress / complete / not_found),
        а `await job.result_info()` — детали результата (не блокируясь и не
        бросая исключение, даже если задача упала).
        """
        redis = await create_pool(settings.arq_redis_settings)
        try:
            job = Job(job_id, redis, _queue_name=settings.ARQ.ARQ_QUEUE_NAME)
            status = await job.status()

            successful = False
            result = None
            if status is JobStatus.complete:
                # Задача завершена. Смотрим детали результата: success может
                # быть False, если задача упала с исключением.
                info = await job.result_info()
                successful = bool(info and info.success)
                result = info.result if successful else None
        finally:
            await redis.close()

        return {
            'task_id': job_id,
            'status': status.name.upper(),  # DEFERRED/QUEUED/IN_PROGRESS/COMPLETE/NOT_FOUND
            'successful': successful,
            'result': result,
        }
