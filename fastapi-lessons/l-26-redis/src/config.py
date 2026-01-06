from typing import Any

from pydantic import RedisDsn, field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='.env'
    )
    REDIS_SERVER: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_USER: str = 'default'
    REDIS_PASSWORD: str
    REDIS_DB: str = "0"

    REDIS_URI: str | None = None

    @field_validator('REDIS_URI', mode='before')
    @classmethod
    def assemble_redis_connection(cls, v: str | None, info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        return str(RedisDsn.build(
            scheme='redis',
            username=info.data.get('REDIS_USER'),
            password=info.data.get('REDIS_PASSWORD'),
            host=info.data.get('REDIS_SERVER'),
            port=info.data.get('REDIS_PORT'),
            path=info.data.get('REDIS_DB') or '0',
        ))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='.env'
    )
    BASE_ROUTE_PATH: str = '/api/v1'
    REDIS: RedisSettings = RedisSettings()


settings = Settings()
