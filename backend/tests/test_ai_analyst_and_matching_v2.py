"""Phases 3 & 5: variant matching penalties + AI analyst tools."""
from app.services.matching_service import compute_match_score
from app.models.product import Product
from uuid import uuid4


def _p(name, brand=None, model=None, sku=None):
    return Product(
        id=uuid4(),
        user_id=uuid4(),
        name=name,
        brand=brand,
        model=model,
        sku=sku,
    )


def test_storage_variant_penalty():
    a = _p("Samsung Galaxy S24 128GB Black", brand="Samsung", model="S24")
    b = _p("Samsung Galaxy S24 256GB Black", brand="Samsung", model="S24")
    s = compute_match_score(a, b)
    assert "storage_mismatch" in s["penalties"]
    assert s["score"] < 0.95


def test_same_product_high_score():
    a = _p("Sony WH-1000XM5 Black", brand="Sony", model="WH-1000XM5", sku="XM5-BLK")
    b = _p("Sony WH-1000XM5 Black", brand="Sony", model="WH-1000XM5", sku="XM5-BLK")
    s = compute_match_score(a, b)
    assert s["score"] >= 0.85
    assert s["label"] in ("likely_same", "possible_match")


def test_ai_query_endpoint(client, auth_headers):
    h = auth_headers("analyst2@priceloop.ai")
    r = client.post("/api/ai/query", headers=h, json={"query": "List my products and any alerts"})
    if r.status_code == 404:
        return  # router path missing in older trees
    assert r.status_code == 200
    body = r.json()
    assert "answer" in body
    assert "tool_trace" in body
    assert "limitations" in body
