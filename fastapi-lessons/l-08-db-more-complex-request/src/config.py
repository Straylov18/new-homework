from typing import Any

from pydantic import field_validator, PostgresDsn
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import SettingsConfigDict, BaseSettings


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


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='.env'
    )
    BASE_ROUTE_PATH: str = '/api/v1'
    DB: DbSettings = DbSettings()


settings = Settings()
