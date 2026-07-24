# Изоляция тестов

Чтобы интеграционные тесты запускались каждый раз на чистой БД, 
нам необходимо изолировать их от основного конфига БД.
Это необходимо например для того, чтобы не было случаев, 
когда в БД уже лежали какие-то данные, и тесты из-за этого отработали не корректено.

Для этого можно например запускать тесты с отдельной конфигурацией БД.

## Использование упрощенной БД для тестовых сценариев

Например при запуске в обычном режиме можно использовать postgres, 
а для запуска тестов можно использовать sqlite, 
для этого нам понадобиться доставить в наш проект `aiosqlite`:
```
poetry add aiosqlite --group test
```

Для того, чтобы удобнее было переключать одну БД на другую можем пока добавить флаг 
`USE_SQLITE: bool = False` в **src/config.py** в настройки БД.
Тогда если он проставлен будем иначе пересобирать `SQLALCHEMY_DATABASE_URI`.
Тогда `DbSettings` будет выглядеть следующим образом:
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

    USE_SQLITE: bool = False

    SQLALCHEMY_DATABASE_URI: str | None = None
    SQLALCHEMY_DATABASE_URI_ASYNC: str | None = None

    PROFILE_QUERY_MODE: bool = False

    @field_validator('SQLALCHEMY_DATABASE_URI', mode='before')
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        if info.data.get('USE_SQLITE'):
            return 'sqlite+aiosqlite:///db.sqlite3'
            # return 'sqlite+aiosqlite:///:memory:'
        else:
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

Теперь наши интеграционные тесты будут запускаться на sqlite БД, 
т.е. не нужно будет поднимать отдельный сервис postgres, мокать функции итд.

Но если приложение завязано на каких-то функциях postgres, которых нет в sqlite 
(стоит понимать, что sqlite достаточно простенький), 
то такой способ не подойдет.

## Использование отдельных настроек запуска приложения для тестов

Можно использовать и другой подход, 
мы можем разворачивать отдельный сервис postgres исключительно для тестов.

Однако в таком случае уже будет не удобно подменять **.env** файлы каджый раз, когда мы хотим запустить тесты или же приложение в обычном режиме.

Мы можем использовать для тестов отдельный **.env** файл.

Чтобы использовать для тестов свои переменные окружения из отдельных .env файлов, установим библиотеку pytest-dotenv:
```shell
poetry add pytest-dotenv --group test
```

Теперь мы создадим для тестов отпдельные .env файл **.test.env**, 
который будет лежать в репозиторие и использоваться только для тестов.
Зададим в нем настройки подключения к другой БД (на порте 5436):
```
USE_SQLITE=false

# Postgres
POSTGRES_SERVER=localhost
POSTGRES_PORT=5436
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=master
```

Чтобы переменный из **.test.env** файла переопределяли отстальные переменные окружения, 
нам необходимо его задать в **pyproject.toml**:
```toml
env_files = ['.test.env']
```

Теперь при запуске тестов можем убедиться, что они не работают со БД по умолчанию.
Таким образом тесты всегда будут запускаться в отдельной БД 
и будут одинаково работать вне зависимости от наполненности основной БД, 
не будут менять данные в основной БД. 

Для запуска тестовой БД в данном уроке предусмотрен отдельный скрипт **start_postgres_in_docker_for_tests.sh**.

## Изоляция каждого теста в своей БД

Теперь же возникает другая проблема, 
даже если наши тесты запускаются в отдельном инстансе постгреса, 
они все еще могут мешать друг другу, если мы будем запускать их в многопоточном режиме (а мы будем, поскольку иначе их запуск будет очень долгим).

Чтобы каждый тест запускался в своей пустой БД:
- мы будем перед каждый запуском интеграционного теста создавать отдельную БД в postgres сервере 
(т.е. будем работать не с дефолтным postgres)
- накатывает миграции на этой БД
- при завершении каждого теста мы будем удалять эту БД, чтобы они не копились

Если бы мы решили в тестовой среде использовать sqlite, 
мы бы просто работали ккждый раз с отдельным файлом БД, 
т.к. sqlite концептуально не поддерживает несколько БД в одном файле.

Здесь мы рассмотрим случай с множеством БД в одном сервере postgres 
(этот вариант более приближен к продакшену, 
поскольку некоторые функции postgres могут не поддерживаться в sqlite).

Весь процесс взаимодействия с БД опишем в виде фикстур, автоматически применяемых ко всем тестам.
Тогда **tests/integration_tests/conftest.py** будет выглядеть следующим образом:
```python
import asyncio
from collections.abc import Iterator
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.config import settings
from src.db.session import async_session_maker
from src.db.session import engine as default_engine
from src.db.session import utf8_serializer
from src.main import app


@pytest.fixture
def async_client() -> AsyncClient:
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test'
    )


def _get_database_url(database: str) -> str:
    if settings.DB.SQLALCHEMY_DATABASE_URI_ASYNC is None:
        raise RuntimeError("Failed to get database url")

    url = make_url(settings.DB.SQLALCHEMY_DATABASE_URI_ASYNC)
    return url.set(database=database).render_as_string(hide_password=False)


async def _create_database(database: str) -> None:
    admin_engine = create_async_engine(
        _get_database_url("postgres"),
        isolation_level="AUTOCOMMIT"
    )

    async with admin_engine.connect() as connection:
        await connection.execute(text(f'CREATE DATABASE "{database}"'))
    await admin_engine.dispose()


async def _drop_database(database: str) -> None:
    admin_engine = create_async_engine(
        _get_database_url("postgres"),
        isolation_level="AUTOCOMMIT"
    )
    async with admin_engine.connect() as connection:
        await connection.execute(
            text(
                """
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = :database
                AND pid <> pg_backend_pid()
                """
            ),
            {"database": database}
        )
        await connection.execute(text(f'DROP DATABASE IF EXISTS "{database}"'))
    await admin_engine.dispose()


def _run_migrations(database_url: str) -> None:
    alembic_config = Config("alembic.ini")
    alembic_config.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(alembic_config, "head")


@pytest.fixture(autouse=True)
def isolated_postgress_db(worker_id: str) -> Iterator[str]:
    database = f"test_{worker_id}_{uuid4().hex}"
    database_url = _get_database_url(database)
    test_engine: AsyncEngine | None = None

    asyncio.run(_create_database(database))

    try:
        _run_migrations(database_url)

        test_engine = create_async_engine(
            database_url,
            echo=settings.DB.POSTGRES_DB_ECHO,
            json_serializer=utf8_serializer
        )
        async_session_maker.configure(bind=test_engine)

        yield database_url
    finally:
        if test_engine is not None:
            asyncio.run(test_engine.dispose())

        async_session_maker.configure(bind=default_engine)
        asyncio.run(_drop_database(database))
```
Здесь:
- при помощи декоработа `@pytest.fixture(autouse=True)` фикстура будет автоматически применяться ко всем тестам
- в фикстере `isolate_postgres_db` мы будем генерировать название временной БД квазислучайным образом
- перед тестом мы будем применять миграции и менятьссылку на БД в генеработе сессий бэкенда (в `isolated_postgress_db` и внутри `try`)
- в конце мы будем подчищять за собой БД (в `finally`)
