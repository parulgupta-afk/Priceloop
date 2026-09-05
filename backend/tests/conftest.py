import os

# Set these BEFORE any app.* module is imported below, since settings are
# read once at import time (pydantic-settings instantiates Settings() at
# module load). This keeps the whole test session on an isolated SQLite
# file instead of ever touching a real Postgres/Redis.
os.environ.setdefault("DATABASE_URL", "sqlite:///./_test_priceloop.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production-use")
os.environ.setdefault("ENVIRONMENT", "development")
# Deliberately unreachable unless a real test Redis happens to be running
# on this port -- this is what lets test_health.py assert the *unreachable*
# path actually gets detected, not just the happy path.
os.environ.setdefault("REDIS_URL", "redis://localhost:1/0")

import pytest
from fastapi.testclient import TestClient

from app.core.database import engine
from app.models.base import Base
from app.main import app


@pytest.fixture(autouse=True)
def clean_database():
    """Every test gets a fresh, empty schema -- no leakage of users/products
    between tests, without the overhead of a new DB file per test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth_headers(client):
    """Registers + logs in a user, returns a ready-to-use Authorization header.
    Call with a distinct email per test to avoid collisions within a test."""

    def _make(email: str = "user@example.com", password: str = "password123"):
        client.post("/api/auth/register", json={"email": email, "password": password})
        r = client.post("/api/auth/login", json={"email": email, "password": password})
        token = r.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _make
