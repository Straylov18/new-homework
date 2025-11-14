# Получение настроек backend приложения из переменных окружения

## Вынесение глобальных переменных в конфиг

В прошлом уроке у нас была одна глобальная переменная в приложении (BASE_ROUTE_PATH).
В больших же проектах у backend приложений существует множество настроечных переменных.
Чтобы было легче задавать такие настроечные переменные, их можно для начала вынести в отдельный конфиг (**src/config.py**).
Опишем настройки нашего приложения через объект унаследованный от класса BaseSettings 
(из пакета **pydantic-settings**, который надо предварительно установить):
```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BASE_ROUTE_PATH: str = '/api/v1'


settings = Settings()
```

Тогда в **main.py** можно просто импортировать объект со всеми нашими настройками.
А все переменные настроек работы проекта будем получать из этого объекта (например так: settings.BASE_ROUTE_PATH).
Тогда **main.py** будет выглядеть следующим образом:
```python
import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

from src.config import settings

print(f'using base prefix: {settings.BASE_ROUTE_PATH}')

app = FastAPI(
    openapi_url=f"{settings.BASE_ROUTE_PATH}/openapi.json",
    docs_url=f"{settings.BASE_ROUTE_PATH}/docs",
)

router = APIRouter(prefix=settings.BASE_ROUTE_PATH)


@router.get('/hello-world')
async def hello_world():
    return "Hi mam!"


app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
```

## Чтение переменных окружения из .env файла

Однако тут возникает проблема. 
Сейчас настройки жестко вшиты в код проекта.
Чтобы проект можно было по-разному разворачивать, не меняя самого кода, 
переменные обычно берутся из "окружения".
Переменные могут браться непосредственно из процесса, под которым работает сессия терминала, 
или же из специального **.env** файла.
Запишем новое значение нашей переменной в **.env** файл.
```python
BASE_ROUTE_PATH="/api/v2"
```

Теперь добавим в **config.py** возможность чтения переменных из этого файла.
Для этого у класса настроек нужно описать специальный параметр (model_config) класса, от которого тот наследуется:
```python
from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='.env'
    )
    BASE_ROUTE_PATH: str = '/api/v1'


settings = Settings()
```

Теперь при запуске проекта переменна BASE_ROUTE_PATH 
возьмется из файла **.env** и будет равна уже "/api/v2", 
а не "/api/v1", как это прописано по умолчанию.

Таким образом данное backend приложение можно будет запускать на разных серверах с разными настройками.
