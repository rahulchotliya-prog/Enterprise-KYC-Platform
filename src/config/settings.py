from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str
    ENV: str
    DEBUG: bool

    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORIGHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    SYNC_DATABASE_URL: str | None = None

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_URL: str
    # class Config:  # Check with comment
    #     env_file = ".env"
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
