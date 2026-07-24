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
