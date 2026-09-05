from functools import lru_cache
# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        extra="ignore",
    )

    app_name: str = "PriceLoop"
    database_url: str = "postgresql://priceloop:priceloop@localhost:5435/priceloop"
    database_url_sync: str = "postgresql://priceloop:priceloop@localhost:5435/priceloop"
    redis_url: str = "redis://localhost:6380/0"
    secret_key: str = "change-me"
    environment: str = "development"
    debug: bool = False
    access_token_expire_minutes: int = 10080
    refresh_token_expire_days: int = 30

    # Comma-separated in .env, e.g. ALLOWED_ORIGINS=https://priceloop.app,https://staging.priceloop.app
    allowed_origins_raw: str = "*"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Stripe -- all blank by default. The app runs fine with billing
    # disabled (checkout endpoint returns a clear error) until these are
    # set to real keys from your Stripe dashboard.
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id_professional: str = ""
    stripe_price_id_enterprise: str = ""
    frontend_url: str = "http://localhost:3000"

    # LLM
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"

    # Scraping & Storage
    scraper_user_agent: str = "PriceLoopBot/1.0"
    scraper_default_rate_limit: float = 1.0
    scraper_max_retries: int = 3
    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "priceloop"

    @property
    def allowed_origins(self) -> list[str]:
        raw = self.cors_origins if self.cors_origins and self.allowed_origins_raw == "*" else self.allowed_origins_raw
        if raw == "*":
            return ["*"]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
