def test_health_live_always_ok(client):
    r = client.get("/health/live")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_health_ready_reports_database_reachable(client):
    r = client.get("/health/ready")
    assert r.json()["checks"]["database"] is True


def test_health_ready_returns_503_when_redis_unreachable(client):
    # conftest.py points REDIS_URL at an address nothing is listening on --
    # this confirms /health/ready actually detects that, not just the happy path.
    r = client.get("/health/ready")
    assert r.status_code == 503
    assert r.json()["checks"]["redis"] is False


def test_legacy_health_endpoint_still_works(client):
    r = client.get("/health")
    assert r.status_code == 200
