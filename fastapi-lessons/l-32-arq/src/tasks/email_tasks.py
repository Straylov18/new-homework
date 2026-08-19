"""
ARQ-задачи для "отправки" писем.

Чтобы не поднимать настоящий SMTP-сервер и не рассылать реальные письма,
"отправка" реализована заглушкой: задача просто ждёт EMAIL_SEND_DELAY_SECONDS
(имитируя сетевую задержку) и пишет строку в текстовый лог-файл.

Это позволяет наглядно увидеть, как:
  - FastAPI кладёт задачи в очередь (Redis);
  - ARQ worker забирает их и выполняет в фоне;
  - результат пишется в файл, не блокируя ответ клиенту.

Все ARQ-задачи — это обычные `async def` функции. Первым аргументом
каждая задача получает `ctx` — контекст воркера, в котором лежит пул
соединений Redis (`ctx['redis']`). Именно через него задачи могут ставить
в очередь другие задачи и читать их результаты.
"""
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import settings

# Логгер ARQ-воркера пишет в stderr и дублирует записи в консоль.
logger = logging.getLogger('arq.email_tasks')


async def _append_to_log_file(message: str) -> None:
    """Дописывает строку в EMAIL_LOG_FILE (создавая каталог при необходимости)."""
    path = Path(settings.EMAIL_LOG_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    loop = asyncio.get_event_loop()
    # Пишем в файл асинхронно (в отдельном потоке), чтобы не блокировать event loop воркера.
    await loop.run_in_executor(None, _write_line, path, message)


def _write_line(path: Path, message: str) -> None:
    """Синхронная запись строки в файл (вызывается в потоке из пула)."""
    with path.open('a', encoding='utf-8') as f:
        f.write(message + '\n')


async def send_email(ctx: dict[str, Any], email: str, subject: str, body: str) -> dict[str, Any]:
    """
    Заглушка отправки одного письма.

    :param ctx:     контекст воркера (передаётся автоматически)
    :param email:   адрес получателя
    :param subject: тема письма
    :param body:    текст письма
    :return:        словарь с результатом (сохраняется в Redis)
    """
    # Имитируем сетевую задержку "отправки". В реальном проекте здесь был бы
    # вызов SMTP-клиента, например aiosmtplib.
    await asyncio.sleep(settings.EMAIL_SEND_DELAY_SECONDS)

    now = datetime.now().isoformat()
    line = f"[{now}] SENT -> {email} | subject={subject} | body={body}"
    await _append_to_log_file(line)
    logger.info("Email sent to %s", email)

    return {
        'email': email,
        'subject': subject,
        'status': 'sent',
        'sent_at': now,
    }


async def send_many_emails(ctx: dict[str, Any], recipients: list[str], subject: str, body: str) -> dict[str, Any]:
    """
    Целевая задача урока: рассылка писем многим пользователям.

    Получает список адресов и для каждого ставит в очередь задачу `send_email`.
    Здесь видна ключевая идея ARQ: задача может вызывать другие задачи
    через `ctx['redis'].enqueue_job(...)`, создавая отдельные подзадачи.

    :param ctx:        контекст воркера (передаётся автоматически)
    :param recipients: список e-mail адресов
    :param subject:    тема письма
    :param body:       текст письма
    :return:           агрегированный результат
    """
    redis = ctx['redis']
    dispatched = []
    for email in recipients:
        # enqueue_job кладёт задачу в очередь без ожидания результата.
        job = await redis.enqueue_job('send_email', email, subject, body)
        dispatched.append({
            'email': email,
            'job_id': job.job_id,
        })

    return {
        'total': len(recipients),
        'dispatched': dispatched,
    }
