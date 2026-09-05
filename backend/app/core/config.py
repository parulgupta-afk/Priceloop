from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ======================
    # Application
    # ======================
    app_name: str = "Priceloop"
    environment: str = "development"
    debug: bool = True
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60
    # Not yet implemented (no refresh-token endpoint exists yet) -- stored
    # now so the setting is ready when that lands, per the roadmap.
    refresh_token_expire_days: int = 30

    # ======================
    # Database
    # ======================
    database_url: str = "postgresql://priceloop:priceloop@postgres:5432/priceloop"

    # ======================
    # Redis / Celery
    # ======================
    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = ""  # falls back to redis_url below if blank
    celery_result_backend: str = ""  # falls back to redis_url below if blank

    # ======================
    # CORS
    # ======================
    # Comma-separated origins the frontend is served from, or "*" for any.
    # Field name must exactly match the env var pydantic-settings looks for --
    # this was previously named allowed_origins_raw / cors_origins_raw, which
    # made it look for ALLOWED_ORIGINS_RAW / CORS_ORIGINS_RAW instead of what
    # was actually in .env. Named directly as "cors_origins" this time so
    # there's no suffix mismatch to get wrong again.
    cors_origins: str = "*"

    # ======================
    # Stripe billing
    # ======================
    # Blank by default -- the app runs fine with billing disabled (checkout
    # endpoint returns a clean 503) until these are set to real keys.
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id_professional: str = ""
    stripe_price_id_enterprise: str = ""
    frontend_url: str = "http://localhost:5173"

    # ======================
    # LLM (reserved -- Phase 15, not called by any code yet)
    # ======================
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # ======================
    # Email (reserved -- Phase 18 notifications, not called by any code yet)
    # ======================
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    emails_from: str = "noreply@priceloop.local"

    # ======================
    # Scraping
    # ======================
    scraper_user_agent: str = "PriceloopBot/1.0"
    scraper_default_rate_limit: float = 1.0
    scraper_max_retries: int = 3

    # ======================
    # Object storage (reserved -- Phase 21 screenshot verification, not called yet)
    # ======================
    s3_endpoint: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_bucket: str = "priceloop"

    class Config:
        env_file = ".env"

    @property
    def cors_origins_list(self) -> list[str]:
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def celery_broker(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def celery_backend(self) -> str:
        return self.celery_result_backend or self.redis_url


settings = Settings()
