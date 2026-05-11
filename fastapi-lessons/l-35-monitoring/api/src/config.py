from typing import Final

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='.env'
    )
    BASE_ROUTE_PATH: str = '/api/v1'
    SECRET_KEY: str = 'no_secrets_here'
    TOKEN_ALGORITHM: str = 'HS256'
    ADMIN_LOGIN: str = 'hello'
    ADMIN_PASSWORD: str = 'its_me'


settings = Settings()

APP_VERSION: Final = '0.1.0'
