from fastapi import FastAPI, BackgroundTasks
from time import sleep

from src.config import settings

app = FastAPI(
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs",
)


def save_text_to_file(text: str):
    sleep(5)
    with open('some_file.json', 'w') as f:
        f.write(text)
    print('file saved')


@app.post('/save-file')
async def save_file(data: dict, background_tasks: BackgroundTasks):
    background_tasks.add_task(save_text_to_file, text=str(data))
    return 5
