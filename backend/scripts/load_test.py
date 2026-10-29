#!/usr/bin/env python3
"""
Simple concurrent load test against PriceLoop API (no Locust required).

Usage:
  python -m scripts.load_test --base http://localhost:8000 --users 10 --requests 50

Records p50/p95 latency and error rate. Do not invent numbers for README —
paste the printed table.
"""
from __future__ import annotations
import argparse
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import httpx
except ImportError:
    raise SystemExit("pip install httpx")


def one_cycle(base: str, email: str, password: str) -> tuple[str, float, int]:
    t0 = time.perf_counter()
    status = 0
    name = "cycle"
    try:
        with httpx.Client(base_url=base, timeout=15.0) as c:
            r = c.post("/api/auth/login", json={"email": email, "password": password})
            if r.status_code != 200:
                # try register once
                c.post("/api/auth/register", json={"email": email, "password": password})
                r = c.post("/api/auth/login", json={"email": email, "password": password})
            status = r.status_code
            if r.status_code != 200:
                return name, (time.perf_counter() - t0) * 1000, status
            token = r.json()["access_token"]
            h = {"Authorization": f"Bearer {token}"}
            r2 = c.get("/api/products/", headers=h)
            status = r2.status_code
            name = "list_products"
            c.get("/health/live")
    except Exception:
        status = 0
    return name, (time.perf_counter() - t0) * 1000, status


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="http://localhost:8000")
    p.add_argument("--users", type=int, default=5)
    p.add_argument("--requests", type=int, default=30)
    p.add_argument("--email", default="loadtest@priceloop.ai")
    p.add_argument("--password", default="LoadTest123!")
    args = p.parse_args()

    # ensure user exists
    try:
        with httpx.Client(base_url=args.base, timeout=10.0) as c:
            c.post("/api/auth/register", json={"email": args.email, "password": args.password})
    except Exception as exc:
        print("warn: register", exc)

    latencies = []
    errors = 0
    t_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=args.users) as pool:
        futs = [
            pool.submit(one_cycle, args.base, args.email, args.password)
            for _ in range(args.requests)
        ]
        for f in as_completed(futs):
            name, ms, status = f.result()
            latencies.append(ms)
            if status == 0 or status >= 400:
                errors += 1
    wall = time.perf_counter() - t_start
    latencies.sort()
    def pct(p):
        if not latencies:
            return 0
        idx = min(len(latencies) - 1, int(len(latencies) * p / 100))
        return round(latencies[idx], 2)
    print("=== PriceLoop load test ===")
    print(f"base={args.base} users={args.users} requests={args.requests}")
    print(f"wall_seconds={wall:.2f}")
    print(f"error_rate={errors}/{len(latencies)}")
    print(f"latency_ms p50={pct(50)} p95={pct(95)} p99={pct(99)} max={round(max(latencies),2) if latencies else 0}")
    print("Paste these measured values into docs — do not invent numbers.")


if __name__ == "__main__":
    main()
