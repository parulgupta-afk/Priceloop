from app.core.security import hash_password, verify_password


def test_register_creates_user(client):
    r = client.post("/api/auth/register", json={"email": "a@example.com", "password": "password123"})
    assert r.status_code == 200
    body = r.json()
    assert body["email"] == "a@example.com"
    assert body["role"] == "USER"
    assert "id" in body


def test_register_duplicate_email_rejected(client):
    client.post("/api/auth/register", json={"email": "dup@example.com", "password": "password123"})
    r = client.post("/api/auth/register", json={"email": "dup@example.com", "password": "different123"})
    assert r.status_code == 400


def test_register_invalid_email_rejected(client):
    r = client.post("/api/auth/register", json={"email": "not-an-email", "password": "password123"})
    assert r.status_code == 422


def test_register_missing_password_rejected(client):
    r = client.post("/api/auth/register", json={"email": "nopass@example.com"})
    assert r.status_code == 422


def test_login_success_returns_jwt(client):
    client.post("/api/auth/register", json={"email": "b@example.com", "password": "password123"})
    r = client.post("/api/auth/login", json={"email": "b@example.com", "password": "password123"})
    assert r.status_code == 200
    assert "access_token" in r.json()
    assert r.json()["token_type"] == "bearer"


def test_login_wrong_password_rejected(client):
    client.post("/api/auth/register", json={"email": "c@example.com", "password": "password123"})
    r = client.post("/api/auth/login", json={"email": "c@example.com", "password": "wrongpass"})
    assert r.status_code == 401


def test_login_nonexistent_user_rejected(client):
    r = client.post("/api/auth/login", json={"email": "ghost@example.com", "password": "password123"})
    assert r.status_code == 401


def test_protected_endpoint_requires_token(client):
    r = client.get("/api/products/")
    assert r.status_code == 401


def test_protected_endpoint_rejects_garbage_token(client):
    r = client.get("/api/products/", headers={"Authorization": "Bearer not-a-real-token"})
    assert r.status_code == 401


def test_me_endpoint_returns_current_user(client, auth_headers):
    headers = auth_headers(email="d@example.com")
    r = client.get("/api/auth/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["email"] == "d@example.com"


def test_me_endpoint_requires_auth(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401


def test_password_is_actually_hashed_not_stored_plaintext():
    hashed = hash_password("mypassword123")
    assert hashed != "mypassword123"
    assert verify_password("mypassword123", hashed) is True
    assert verify_password("wrongpassword", hashed) is False
