def test_health_live_always_ok(client):
    r = client.get("/health/live")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_health_ready_reports_database_reachable(client):
    r = client.get("/health/ready")
    assert r.json()["checks"]["database"] is True


def test_health_ready_returns_200_when_dependencies_healthy(client, monkeypatch):
    import redis

    class MockRedis:
        def ping(self):
            return True

        def close(self):
            pass

    monkeypatch.setattr(redis, "from_url", lambda *args, **kwargs: MockRedis())
    r = client.get("/health/ready")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["checks"]["database"] is True
    assert r.json()["checks"]["redis"] is True


def test_health_ready_returns_503_when_redis_unreachable(client, monkeypatch):
    # Ensure REDIS_URL points to an unreachable port even if external Redis is running in CI/host
    from app.core.config import settings
    monkeypatch.setattr(settings, "redis_url", "redis://127.0.0.1:1/0")
    r = client.get("/health/ready")
    assert r.status_code == 503
    assert r.json()["status"] == "unavailable"
    assert r.json()["checks"]["redis"] is False


def test_health_ready_returns_503_when_database_unreachable(client, monkeypatch):
    from app.core import database

    def _fail_connect(*args, **kwargs):
        raise Exception("Database connection failed")

    monkeypatch.setattr(database.engine, "connect", _fail_connect)
    r = client.get("/health/ready")
    assert r.status_code == 503
    assert r.json()["status"] == "unavailable"
    assert r.json()["checks"]["database"] is False


def test_legacy_health_endpoint_still_works(client):
    r = client.get("/health")
    assert r.status_code == 200

