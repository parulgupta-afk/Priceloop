def test_new_user_defaults_to_free_plan(client, auth_headers):
    headers = auth_headers(email="billing1@example.com")
    r = client.get("/api/billing/subscription", headers=headers)
    assert r.status_code == 200
    assert r.json()["plan"] == "FREE"
    assert r.json()["status"] == "NONE"


def test_subscription_requires_auth(client):
    r = client.get("/api/billing/subscription")
    assert r.status_code == 401


def test_checkout_fails_cleanly_when_stripe_unconfigured(client, auth_headers):
    headers = auth_headers(email="billing2@example.com")
    r = client.post("/api/billing/create-checkout-session", json={"plan": "professional"}, headers=headers)
    assert r.status_code == 503, "must fail cleanly, not crash, when Stripe keys aren't set"


def test_checkout_rejects_unknown_plan_name(client, auth_headers, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "stripe_secret_key", "sk_test_fake_for_testing")
    headers = auth_headers(email="billing3@example.com")
    r = client.post("/api/billing/create-checkout-session", json={"plan": "deluxe"}, headers=headers)
    assert r.status_code == 400


def test_webhook_activates_subscription_on_checkout_completed(client, auth_headers, monkeypatch):
    from app.core.config import settings
    from app.services import billing_service

    monkeypatch.setattr(settings, "stripe_secret_key", "sk_test_fake_for_testing")
    monkeypatch.setattr(settings, "stripe_webhook_secret", "whsec_fake_for_testing")

    headers = auth_headers(email="billing4@example.com")
    user_id = client.get("/api/auth/me", headers=headers).json()["id"]
    client.get("/api/billing/subscription", headers=headers)  # lazily creates the FREE row

    fake_event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "client_reference_id": user_id,
                "customer": "cus_fake",
                "subscription": "sub_fake",
                "metadata": {"user_id": user_id, "plan": "professional"},
            }
        },
    }
    # Only the Stripe-server-side signature check is mocked -- everything
    # downstream (the DB update logic) runs for real.
    monkeypatch.setattr(billing_service.stripe.Webhook, "construct_event", lambda *a, **kw: fake_event)

    r = client.post("/api/billing/webhook", content=b"{}", headers={"stripe-signature": "fake"})
    assert r.status_code == 200

    r = client.get("/api/billing/subscription", headers=headers)
    assert r.json()["plan"] == "PROFESSIONAL"
    assert r.json()["status"] == "ACTIVE"


def test_webhook_cancellation_reverts_to_free(client, auth_headers, monkeypatch):
    from app.core.config import settings
    from app.services import billing_service

    monkeypatch.setattr(settings, "stripe_secret_key", "sk_test_fake_for_testing")
    monkeypatch.setattr(settings, "stripe_webhook_secret", "whsec_fake_for_testing")

    headers = auth_headers(email="billing5@example.com")
    user_id = client.get("/api/auth/me", headers=headers).json()["id"]
    client.get("/api/billing/subscription", headers=headers)

    activate_event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "client_reference_id": user_id,
                "customer": "cus_fake2",
                "subscription": "sub_fake2",
                "metadata": {"user_id": user_id, "plan": "enterprise"},
            }
        },
    }
    monkeypatch.setattr(billing_service.stripe.Webhook, "construct_event", lambda *a, **kw: activate_event)
    client.post("/api/billing/webhook", content=b"{}", headers={"stripe-signature": "fake"})

    cancel_event = {
        "type": "customer.subscription.deleted",
        "data": {"object": {"id": "sub_fake2", "status": "canceled"}},
    }
    monkeypatch.setattr(billing_service.stripe.Webhook, "construct_event", lambda *a, **kw: cancel_event)
    r = client.post("/api/billing/webhook", content=b"{}", headers={"stripe-signature": "fake"})
    assert r.status_code == 200

    r = client.get("/api/billing/subscription", headers=headers)
    assert r.json()["plan"] == "FREE"
    assert r.json()["status"] == "CANCELED"
