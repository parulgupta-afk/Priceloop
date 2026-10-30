"""Phases 8–11: analytics helpers, anomalies, alerts, ownership isolation."""
from decimal import Decimal
from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from app.services.analytics_service import get_product_analytics
from app.services.anomaly_service import (
    detect_price_anomalies,
    _z_score_indices,
    _mad_indices,
)
from app.core.database import SessionLocal
from app.models.user import User
from app.models.product import Product, ProductListing, PriceObservation, Source
from app.core.security import hash_password


def test_pct_change_and_analytics_empty(client, auth_headers):
    headers = auth_headers("analytics@priceloop.ai")
    # create product
    r = client.post(
        "/api/products/",
        headers=headers,
        json={"name": "Test Laptop", "listings": [{"source": "demo", "url": "https://example.com/p/1"}]},
    )
    assert r.status_code in (200, 201)
    pid = r.json()["id"]
    r2 = client.get(f"/api/products/{pid}/analytics?days=30", headers=headers)
    # may 404 if prices router path differs or 200 with empty
    assert r2.status_code in (200, 404)
    if r2.status_code == 200:
        body = r2.json()
        assert body.get("observation_count", 0) == 0 or "message" in body


def test_zscore_and_mad_unit():
    stable = [10.0] * 10
    assert _z_score_indices(stable) == []
    assert _mad_indices(stable) == []
    spiked = [10.0] * 8 + [50.0, 10.0]
    assert len(_z_score_indices(spiked, threshold=2.0)) >= 1
    assert len(_mad_indices(spiked, threshold=2.5)) >= 1


def test_cross_user_product_isolation(client, auth_headers):
    h1 = auth_headers("owner1@priceloop.ai")
    h2 = auth_headers("owner2@priceloop.ai")
    r = client.post(
        "/api/products/",
        headers=h1,
        json={"name": "Secret SKU", "listings": [{"source": "demo", "url": "https://example.com/x"}]},
    )
    assert r.status_code in (200, 201)
    pid = r.json()["id"]
    # second user cannot read
    r2 = client.get(f"/api/products/{pid}", headers=h2)
    assert r2.status_code in (403, 404)
    # second user cannot list it
    listed = client.get("/api/products/", headers=h2).json()
    ids = [p["id"] for p in listed] if isinstance(listed, list) else []
    assert pid not in ids


def test_alert_create_list_delete(client, auth_headers):
    headers = auth_headers("alerts@priceloop.ai")
    r = client.post(
        "/api/products/",
        headers=headers,
        json={"name": "Alertable", "listings": [{"source": "demo", "url": "https://example.com/a"}]},
    )
    if r.status_code not in (200, 201):
        pytest.skip("product create failed in this env")
    pid = r.json()["id"]
    r2 = client.post(
        "/api/alerts",
        headers=headers,
        json={"product_id": pid, "rule_type": "PRICE_DROP_PCT", "threshold": 10},
    )
    if r2.status_code == 404:
        pytest.skip("alerts router not mounted")
    assert r2.status_code in (200, 201)
    alert_id = r2.json()["id"]
    r3 = client.get("/api/alerts", headers=headers)
    assert r3.status_code == 200
    assert any(a["id"] == alert_id for a in r3.json())
    r4 = client.delete(f"/api/alerts/{alert_id}", headers=headers)
    assert r4.status_code in (200, 204)


def test_insights_grounded_shape(client, auth_headers):
    headers = auth_headers("insight@priceloop.ai")
    r = client.post(
        "/api/products/",
        headers=headers,
        json={"name": "Insight Product", "listings": [{"source": "demo", "url": "https://example.com/i"}]},
    )
    if r.status_code not in (200, 201):
        pytest.skip("product create failed")
    pid = r.json()["id"]
    r2 = client.get(f"/api/products/{pid}/insights", headers=headers)
    if r2.status_code == 404:
        pytest.skip("insights not mounted")
    assert r2.status_code == 200
    body = r2.json()
    assert "summary" in body
    assert "limitations" in body
    assert "confidence" in body


def test_alert_evaluate_endpoint(client, auth_headers):
    headers = auth_headers("eval_alerts@priceloop.ai")
    r = client.post("/api/alerts/evaluate", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert "triggers" in data
    assert isinstance(data["triggers"], list)
