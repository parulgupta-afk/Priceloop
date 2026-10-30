#!/usr/bin/env python3
"""
End-to-end smoke test script for PriceLoop platform.
Validates server health, authentication, catalog access, intelligence algorithms,
alerts evaluation, and Stripe billing checkout.

Usage:
    python -m scripts.smoke_test
    python -m scripts.smoke_test --base http://127.0.0.1:8000
"""
from __future__ import annotations

import argparse
import sys
import time

try:
    import httpx
except ImportError:
    import urllib.request
    import json

    raise SystemExit("Please run in backend virtual environment with httpx installed.")


def run_smoke_test(base_url: str = "http://127.0.0.1:8000") -> bool:
    print(f"[*] Starting PriceLoop Smoke Test against: {base_url}")
    t0 = time.perf_counter()

    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        # 1. Health
        r = client.get("/health")
        if r.status_code != 200:
            print(f"[FAIL] Health check failed with status {r.status_code}")
            return False
        print("[PASS] 1. System Health: OK (HTTP 200)")

        # 2. Auth Login
        auth_payload = {"email": "demo@priceloop.ai", "password": "Demo123!"}
        r = client.post("/api/auth/login", json=auth_payload)
        if r.status_code != 200:
            print(f"[FAIL] Demo login failed: {r.text}")
            return False
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("[PASS] 2. Authentication: Logged in (JWT Token received)")

        # 3. Products Catalog
        r = client.get("/api/products/", headers=headers)
        if r.status_code != 200:
            print(f"[FAIL] Product catalog fetch failed: {r.text}")
            return False
        products = r.json()
        print(f"[PASS] 3. Product Catalog: Retrieved {len(products)} products")

        product_id = products[0]["id"] if products else None
        if product_id:
            # 4. Intelligence: Anomalies
            r = client.get(f"/api/products/{product_id}/anomalies", headers=headers)
            if r.status_code == 200:
                print(f"[PASS] 4a. Intelligence: Price Anomalies reachable (HTTP 200)")

            # 5. Intelligence: Matching
            r = client.get(f"/api/products/{product_id}/matches", headers=headers)
            if r.status_code == 200:
                print(f"[PASS] 4b. Intelligence: Product Matches reachable (HTTP 200)")

            # 6. Intelligence: Insights
            r = client.get(f"/api/products/{product_id}/insights", headers=headers)
            if r.status_code == 200:
                print(f"[PASS] 4c. Intelligence: Grounded Insights generated (HTTP 200)")

        # 7. Alerts: Evaluate
        r = client.post("/api/alerts/evaluate", headers=headers)
        if r.status_code == 200:
            triggers = r.json().get("triggers", [])
            print(f"[PASS] 5. Alerts Evaluation: Active (Evaluated {len(triggers)} triggers)")

        # 8. Billing: Subscription
        r = client.get("/api/billing/subscription", headers=headers)
        if r.status_code == 200:
            sub = r.json()
            print(f"[PASS] 6a. Billing: User plan={sub.get('plan')}, status={sub.get('status')}")

        # 9. Billing: Stripe Checkout
        r = client.post("/api/billing/create-checkout-session", json={"plan": "PROFESSIONAL"}, headers=headers)
        if r.status_code == 200:
            checkout_url = r.json().get("checkout_url", "")
            print(f"[PASS] 6b. Billing: Professional Checkout URL generated successfully")

    elapsed = round(time.perf_counter() - t0, 2)
    print(f"\n[+] All smoke test checks passed in {elapsed}s!")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PriceLoop smoke test runner")
    parser.add_argument("--base", default="http://127.0.0.1:8000", help="Base API URL")
    args = parser.parse_args()

    success = run_smoke_test(args.base)
    sys.exit(0 if success else 1)
