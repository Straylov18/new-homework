from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='../.env'
    )
    BASE_ROUTE_PATH: str = '/api/v1'
    SQLALCHEMY_DATABASE_URL: str = "sqlite+aiosqlite:///db.sqlite3"


settings = Settings()
