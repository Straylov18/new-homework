from fastapi import FastAPI, BackgroundTasks
from time import sleep
import asyncio

from src.config import settings

app = FastAPI(
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs",
)


def save_text_to_file(text: str):
    sleep(5)
    with open('some_file.json', 'w') as f:
        f.write(text)
    print('файл сохранен')


@app.post('/save-file')
async def save_file(data: dict, background_tasks: BackgroundTasks):
    background_tasks.add_task(save_text_to_file, text=str(data))
    return 5


async def some_async_task(sleep_time: int):
    await asyncio.sleep(sleep_time)
    print(f'результат после {sleep_time} секунд')


@app.get('/run-async-task')
async def save_file(sleep_time: int):
    asyncio.create_task(some_async_task(sleep_time))
    return f'вывод логов произойдет через {sleep_time} секунд'
