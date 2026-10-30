"""Unit tests for product matching score."""

from types import SimpleNamespace

from app.services.matching_service import compute_match_score


def _product(name, brand=None, model=None):
    return SimpleNamespace(name=name, brand=brand, model=model)


def test_high_confidence_same_product():
    a = _product("Sony WH-1000XM5 Wireless Headphones Black", brand="Sony", model="WH-1000XM5")
    b = _product("Sony WH1000XM5 Bluetooth Headphones - Black", brand="Sony", model="WH1000XM5")
    score = compute_match_score(a, b)
    assert score["confidence"] >= 0.75
    assert score["level"] in ("HIGH", "MEDIUM")


def test_low_confidence_different_products():
    a = _product("Sony WH-1000XM5", brand="Sony", model="WH-1000XM5")
    b = _product("Apple AirPods Pro 2", brand="Apple", model="AirPods Pro")
    score = compute_match_score(a, b)
    assert score["confidence"] < 0.75
    assert score["level"] == "LOW"


def test_exact_product_match_score():
    a = _product("Sony WH-1000XM5", brand="Sony", model="WH-1000XM5")
    b = _product("Sony WH-1000XM5", brand="Sony", model="WH-1000XM5")
    score = compute_match_score(a, b)
    assert score["confidence"] >= 0.95
    assert score["level"] == "HIGH"
    assert score["components"]["brand_match"] == 1.0


def test_matching_handles_none_brand_and_model():
    a = _product("Dell UltraSharp U2723QE 27 Inch 4K UHD")
    b = _product("Dell UltraSharp Monitor 27 4K")
    score = compute_match_score(a, b)
    assert "confidence" in score
    assert "components" in score
    assert score["components"]["brand_match"] == 1.0
