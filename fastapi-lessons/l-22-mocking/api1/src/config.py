from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='.env'
    )
    BASE_ROUTE_PATH: str = '/api/v1'
    AUTH_SERVER_ADDRESS: str = 'http://127.0.0.1:8001/api/v1'


settings = Settings()
