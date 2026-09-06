import pytest

from app.core.config import Settings


def test_production_fails_when_secret_key_is_default_or_short():
    with pytest.raises(ValueError, match="SECRET_KEY"):
        s = Settings(
            environment="production",
            secret_key="change-me",
            database_url="postgresql://user:pass@localhost:5432/db",
            redis_url="redis://localhost:6379/0",
            cors_origins="https://priceloop.app",
        )
        s.validate_production()

    with pytest.raises(ValueError, match="SECRET_KEY"):
        s = Settings(
            environment="production",
            secret_key="short",
            database_url="postgresql://user:pass@localhost:5432/db",
            redis_url="redis://localhost:6379/0",
            cors_origins="https://priceloop.app",
        )
        s.validate_production()


def test_production_fails_when_database_url_is_sqlite():
    with pytest.raises(ValueError, match="PostgreSQL DATABASE_URL"):
        s = Settings(
            environment="production",
            secret_key="a" * 32,
            database_url="sqlite:///./prod.db",
            redis_url="redis://localhost:6379/0",
            cors_origins="https://priceloop.app",
        )
        s.validate_production()


def test_production_fails_when_database_url_is_missing():
    with pytest.raises(ValueError, match="PostgreSQL DATABASE_URL"):
        s = Settings(
            environment="production",
            secret_key="a" * 32,
            database_url="",
            redis_url="redis://localhost:6379/0",
            cors_origins="https://priceloop.app",
        )
        s.validate_production()


def test_production_fails_when_redis_url_is_missing_or_invalid():
    with pytest.raises(ValueError, match="REDIS_URL"):
        s = Settings(
            environment="production",
            secret_key="a" * 32,
            database_url="postgresql://user:pass@localhost:5432/db",
            redis_url="",
            cors_origins="https://priceloop.app",
        )
        s.validate_production()

    with pytest.raises(ValueError, match="REDIS_URL"):
        s = Settings(
            environment="production",
            secret_key="a" * 32,
            database_url="postgresql://user:pass@localhost:5432/db",
            redis_url="http://not-redis:6379",
            cors_origins="https://priceloop.app",
        )
        s.validate_production()


def test_production_fails_when_cors_origins_is_wildcard_or_empty():
    with pytest.raises(ValueError, match="CORS_ORIGINS"):
        s = Settings(
            environment="production",
            secret_key="a" * 32,
            database_url="postgresql://user:pass@localhost:5432/db",
            redis_url="redis://localhost:6379/0",
            cors_origins="*",
            allowed_origins_raw="*",
        )
        s.validate_production()

    with pytest.raises(ValueError, match="CORS_ORIGINS"):
        s = Settings(
            environment="production",
            secret_key="a" * 32,
            database_url="postgresql://user:pass@localhost:5432/db",
            redis_url="redis://localhost:6379/0",
            cors_origins="",
            allowed_origins_raw="",
        )
        s.validate_production()


def test_production_fails_when_s3_uses_minioadmin():
    with pytest.raises(ValueError, match="minioadmin"):
        s = Settings(
            environment="production",
            secret_key="a" * 32,
            database_url="postgresql://user:pass@localhost:5432/db",
            redis_url="redis://localhost:6379/0",
            cors_origins="https://priceloop.app",
            s3_endpoint="http://minio:9000",
            s3_access_key="minioadmin",
            s3_secret_key="minioadmin",
        )
        s.validate_production()


def test_production_succeeds_with_valid_config():
    s = Settings(
        environment="production",
        secret_key="a" * 32,
        database_url="postgresql://user:pass@localhost:5432/db",
        redis_url="redis://localhost:6379/0",
        cors_origins="https://priceloop.app,https://staging.priceloop.app",
        s3_endpoint="",
    )
    s.validate_production()
    assert s.allowed_origins == ["https://priceloop.app", "https://staging.priceloop.app"]

    # Also test with valid S3 credentials
    s_with_s3 = Settings(
        environment="production",
        secret_key="b" * 32,
        database_url="postgresql://user:pass@localhost:5432/db",
        redis_url="redis://localhost:6379/0",
        cors_origins="https://priceloop.app",
        s3_endpoint="https://s3.us-east-1.amazonaws.com",
        s3_access_key="AKIAREALPRODKEY",
        s3_secret_key="RealProdSecretKeyNotDefaultAdmin",
    )
    s_with_s3.validate_production()



def test_development_allows_safe_local_defaults():
    s = Settings(
        environment="development",
        secret_key="change-me",
        database_url="sqlite:///./test.db",
        redis_url="redis://localhost:6380/0",
        cors_origins="*",
    )
    # Does not raise
    s.validate_production()
    assert s.allowed_origins == ["*"]
