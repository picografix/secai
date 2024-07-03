from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "getData API"
    REDIS_URL: str = "redis://localhost:6379/0"
    DATABASE_URL: str = "postgresql://postgres:mysecretpassword@localhost:5432/postgres"

settings = Settings()