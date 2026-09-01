from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://priceloop:priceloop@postgres:5432/priceloop"
    redis_url: str = "redis://redis:6379/0"
    secret_key: str = "change-me"
    environment: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()
