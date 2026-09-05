import uuid


def test_create_product_requires_auth(client):
    r = client.post("/api/products/", json={"name": "Test", "listings": []})
    assert r.status_code == 401


def test_create_and_get_product(client, auth_headers):
    headers = auth_headers(email="owner@example.com")
    r = client.post(
        "/api/products/",
        json={
            "name": "Sony WH-1000XM5",
            "brand": "Sony",
            "category": "Electronics",
            "listings": [{"source": "amazon", "url": "https://amazon.com/x", "tracking_frequency_minutes": 60}],
        },
        headers=headers,
    )
    assert r.status_code == 200
    product = r.json()
    assert product["name"] == "Sony WH-1000XM5"
    assert len(product["listings"]) == 1
    assert product["listings"][0]["source"] == "amazon"

    r = client.get(f"/api/products/{product['id']}", headers=headers)
    assert r.status_code == 200
    assert r.json()["name"] == "Sony WH-1000XM5"


def test_create_product_with_no_listings_allowed(client, auth_headers):
    headers = auth_headers(email="minimal@example.com")
    r = client.post("/api/products/", json={"name": "Bare product", "listings": []}, headers=headers)
    assert r.status_code == 200
    assert r.json()["listings"] == []


def test_list_products_only_shows_own(client, auth_headers):
    headers_a = auth_headers(email="alice@example.com")
    headers_b = auth_headers(email="bob@example.com")

    client.post("/api/products/", json={"name": "Alice's product", "listings": []}, headers=headers_a)

    r = client.get("/api/products/", headers=headers_b)
    assert r.status_code == 200
    assert r.json() == []

    r = client.get("/api/products/", headers=headers_a)
    assert len(r.json()) == 1


def test_cannot_fetch_another_users_product_by_id(client, auth_headers):
    headers_a = auth_headers(email="alice2@example.com")
    headers_b = auth_headers(email="bob2@example.com")

    r = client.post("/api/products/", json={"name": "Private", "listings": []}, headers=headers_a)
    product_id = r.json()["id"]

    r = client.get(f"/api/products/{product_id}", headers=headers_b)
    assert r.status_code == 404, "cross-tenant access must 404, not leak another user's data"


def test_get_nonexistent_product_returns_404(client, auth_headers):
    headers = auth_headers(email="e@example.com")
    r = client.get(f"/api/products/{uuid.uuid4()}", headers=headers)
    assert r.status_code == 404


def test_malformed_product_id_returns_422_not_500(client, auth_headers):
    headers = auth_headers(email="f@example.com")
    r = client.get("/api/products/not-a-uuid", headers=headers)
    assert r.status_code == 422


def test_create_product_missing_name_returns_422(client, auth_headers):
    headers = auth_headers(email="g@example.com")
    r = client.post("/api/products/", json={"listings": []}, headers=headers)
    assert r.status_code == 422
