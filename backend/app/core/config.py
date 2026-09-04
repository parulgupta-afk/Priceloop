from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://priceloop:priceloop@postgres:5432/priceloop"
    redis_url: str = "redis://redis:6379/0"
    secret_key: str = "change-me"
    environment: str = "development"
    # Comma-separated in .env, e.g. ALLOWED_ORIGINS=https://priceloop.app,https://staging.priceloop.app
    allowed_origins_raw: str = "*"

    # Stripe -- all blank by default. The app runs fine with billing
    # disabled (checkout endpoint returns a clear error) until these are
    # set to real keys from your Stripe dashboard.
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id_professional: str = ""
    stripe_price_id_enterprise: str = ""
    frontend_url: str = "http://localhost:5173"

    class Config:
        env_file = ".env"

    @property
    def allowed_origins(self) -> list[str]:
        if self.allowed_origins_raw == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins_raw.split(",")]


settings = Settings()
