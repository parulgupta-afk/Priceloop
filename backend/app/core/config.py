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

    # Comma-separated in .env, e.g. CORS_ORIGINS=https://priceloop.app,https://staging.priceloop.app
    allowed_origins_raw: str = ""
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
    s3_endpoint: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_bucket: str = "priceloop"

    # Email
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    emails_from: str = "noreply@priceloop.local"

    # Celery
    celery_broker_url: str = ""
    celery_result_backend: str = ""

    def validate_production(self) -> None:
        """Explicit validation called on startup or Settings initialization for production."""
        if self.environment.lower() != "production":
            return

        weak = {
            "",
            "change-me",
            "changeme",
            "secret",
            "dev",
            "test",
            "password",
            "change-me-to-a-long-random-string-in-production",
        }
        if not self.secret_key or self.secret_key.strip().lower() in weak or len(self.secret_key) < 32:
            raise ValueError(
                "Production requires SECRET_KEY to be a strong random string "
                "(at least 32 characters). Set SECRET_KEY in the environment."
            )

        if not self.database_url or self.database_url.startswith("sqlite"):
            raise ValueError(
                "Production requires a PostgreSQL DATABASE_URL. SQLite is not allowed in production."
            )
        if not (self.database_url.startswith("postgresql://") or self.database_url.startswith("postgres://")):
            raise ValueError(
                "Production DATABASE_URL must be a PostgreSQL connection string (postgresql://...)."
            )

        if not self.redis_url or not (self.redis_url.startswith("redis://") or self.redis_url.startswith("rediss://")):
            raise ValueError(
                "Production requires a valid REDIS_URL starting with redis:// or rediss://."
            )

        origins = self.cors_origins_list
        if not origins or "*" in origins:
            raise ValueError(
                "Production requires explicit CORS_ORIGINS. Wildcard '*' is not permitted in production."
            )

        if self.s3_endpoint:
            if self.s3_access_key.lower() == "minioadmin" or self.s3_secret_key.lower() == "minioadmin":
                raise ValueError(
                    "Production cannot use default MinIO credentials ('minioadmin'). Configure secure S3 keys or unset S3_ENDPOINT."
                )

    @property
    def allowed_origins(self) -> list[str]:
        raw = self.cors_origins or self.allowed_origins_raw
        if self.environment.lower() == "production":
            if not raw or raw.strip() == "*":
                return []
            return [origin.strip() for origin in raw.split(",") if origin.strip() and origin.strip() != "*"]
        if not raw or raw.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]

    @property
    def cors_origins_list(self) -> list[str]:
        return self.allowed_origins

    @property
    def celery_broker(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def celery_backend(self) -> str:
        return self.celery_result_backend or self.redis_url


@lru_cache()
def get_settings() -> Settings:
    s = Settings()
    if s.environment.lower() == "production":
        s.validate_production()
    return s


settings = get_settings()
