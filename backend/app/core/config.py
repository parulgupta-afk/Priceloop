from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://priceloop:priceloop@postgres:5432/priceloop"
    redis_url: str = "redis://redis:6379/0"
    secret_key: str = "change-me"
    environment: str = "development"
    # Comma-separated in .env, e.g. ALLOWED_ORIGINS=https://priceloop.app,https://staging.priceloop.app
    allowed_origins_raw: str = "*"

    class Config:
        env_file = ".env"

    @property
    def allowed_origins(self) -> list[str]:
        if self.allowed_origins_raw == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins_raw.split(",")]


settings = Settings()
