from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME : str
    ENV : str
    DEBUG : bool

    class Config:  # Check with comment
        env_file = ".env"


settings = Settings()