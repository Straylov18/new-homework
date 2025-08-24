# Использование PostgreSQL в качестве БД

SQLite обычно используется для запуска на небольших устройствах, 
когда к БД не будет обслуживать больше одного соединения. 

Для полноценного backend приложения же удобнее использовать другие БД.
Одной из наиболее популярных на данный момент является PostgreSQL.

Ее также удобно использовать для локальной разработки, поскольку к ней удобнее параллельно подключаться через БД-клиентское приложение (например pgadmin). 

Поэтому начиная с этого урока в качестве реляционной БД будет использоваться именно postgres.

## Запуск БД postgres в докере

Postgres можно развернуть отдельно как сервис, однако для разработки удобнее запускать его в Docker контейнере.

В случае запуска postgres в docker контейнере он также разворачивается как сервис на своем стандартном порту 5432, 
просто внутри контейнера, в котором он уже предустановлен и не требует настройки.

Базовые знания о docker контейнерах можно получить тут: 
[введение в docker](https://github.com/TheYeniseiTrireme/homework-materials/tree/main/docker-basics/README.md).

Чтобы не мучатся с установкой postgres и запуском его на твоей системе, 
можешь запустить его из специального docker образа **postgres**:
```shell
docker run -d -p 5435:5432 -e POSTGRES_PASSWORD=master postgres:16
```
Рассмотрим параметры данного запуска docker контейнера:
- **-d** запустит контейнер в фоновом режиме (без перехватывания управления консоли)
- **-p 5435:5432** означает, что сервисы работающие внутри на порту 5432 (postgres БД в нашем случае), будут доступны снаружи на порту 5435
- **-e POSTGRES_PASSWORD=master** передает пароль от основного пользователя в качестве переменной окружения (postgres же в свою очередь подтянет ее при запуске внуткри контейнера)
- **postgres:16** означает, что контейнер будет сделан на основе образа postgres 16-й версии

При таком запуске БД будет чистится каждый перезапуск контейнера,
что удобно для разработки.
Если нужно, чтобы БД оставалась одной и той же каждый перезапуск, 
можно добавить volume при запуске контейнера, 
чтобы postgres мог сохранять все данные на диск, 
но об этом в следующих уроках.

Чтобы было удобнее можешь добавить команды перезапуска docker контейнера в bash скрипт и запускать его:
```shell
./start_postgres_in_docker.sh
```

Чтобы убедиться, что контейнер действительно стартовал, 
выведи список всех работающих контейнеров:
```shell
docker ps
```
После этого в табличке найди контейнер, 
который был создан из образа postgres:16.

При необходимости можешь его остановить по ID:
```shell
docker stop $CONTAINER_ID
```

## Использование БД postgres в python приложении

Чтобы python приложение могло работать с БД postgres, ему понадобится еще одна библиотека:
```shell
poetry add psycopg
```

Подключение к БД postgres требует отдельного пользователя в БД с паролем.
Также одна БД postgres может иметь в себе несколько БД для разных проектов или разных микросервисов.
Таким образом при подключении к postgres придется указать еще:
- имя пользователя в БД
- его пароль
- имя БД, с которой будет производиться работа

Поскольку настроек БД становится сильно больше, их лучше описать в отдельном классе в **config.py**:
```python
class DbSettings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='.env'
    )
    POSTGRES_SERVER: str = 'localhost'
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "postgres"
    POSTGRES_DB_ECHO: bool = True

    SQLALCHEMY_DATABASE_URI: str | None = None
    SQLALCHEMY_DATABASE_URI_ASYNC: str | None = None

    PROFILE_QUERY_MODE: bool = False

    @field_validator('SQLALCHEMY_DATABASE_URI', mode='before')
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        return str(PostgresDsn.build(
            scheme='postgresql+psycopg',
            username=info.data.get('POSTGRES_USER'),
            password=info.data.get('POSTGRES_PASSWORD'),
            host=info.data.get('POSTGRES_SERVER'),
            port=info.data.get('POSTGRES_PORT'),
            path=info.data.get('POSTGRES_DB') or '',
        ))

    @field_validator('SQLALCHEMY_DATABASE_URI_ASYNC', mode='before')
    @classmethod
    def assemble_async_db_connection(cls, v: str | None, info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        return info.data.get('SQLALCHEMY_DATABASE_URI')
```

Пусть также для удобства объект настроек БД будет лежать в объекте общих настроек:
```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='.env'
    )
    BASE_ROUTE_PATH: str = '/api/v1'
    DB: DbSettings = DbSettings()
```

Теперь в коде проекта необходимо заменить "settings.SQLALCHEMY_DATABASE_URL" на "settings.DB.SQLALCHEMY_DATABASE_URI".

После данных операций можно точно так же накатить миграции:
```shell
poetry run alembic upgrade head
```

И запустить проект:
```shell
poetry run uvicorn src.main:app
```

Теперь ты можешь параллельно с работой приложения спокойно подключаться к БД через SQL клиент.
Такие клиенты обычно встроены в IDE или же их можно скачать отдельно.
Для БД postgres существует также специализированный клиент pgadmin, его можно скачать на официальном сайте postgres.
