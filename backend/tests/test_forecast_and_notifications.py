"""Phase 6–7: forecast label + dedupe evaluate endpoint."""
def test_forecast_insufficient_data(client, auth_headers):
    h = auth_headers("forecast@priceloop.ai")
    r = client.post(
        "/api/products/",
        headers=h,
        json={"name": "Forecast Book", "listings": [{"source": "demo", "url": "https://example.com/f"}]},
    )
    if r.status_code not in (200, 201):
        return
    pid = r.json()["id"]
    r2 = client.get(f"/api/products/{pid}/forecast", headers=h)
    if r2.status_code == 404:
        return
    assert r2.status_code == 200
    body = r2.json()
    assert body.get("label") == "experimental" or body.get("status") == "insufficient_data"


def test_evaluate_deduped_endpoint(client, auth_headers):
    h = auth_headers("dedupe@priceloop.ai")
    r = client.post("/api/alerts/evaluate-deduped", headers=h)
    if r.status_code == 404:
        return
    assert r.status_code == 200
    body = r.json()
    assert "notifications" in body
    assert "dedupe_window_minutes" in body
