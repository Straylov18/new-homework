# Использование PostgreSQL в качестве БД

[//]: # (TODO плюсы работы с postgres)

## Запуск БД postgres в докере

[//]: # (TODO)

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
