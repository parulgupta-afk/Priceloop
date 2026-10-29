"""
Sync demo seed for SQLite/Postgres (matches SessionLocal stack).

  cd backend && python -m scripts.seed_demo_sync

Creates demo@priceloop.ai / Demo123! with sample products, listings, and price history.
"""
from __future__ import annotations
import random
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent))

from app.core.database import SessionLocal, engine
from app.core.security import hash_password
from app.models.base import Base
from app.models.user import User
from app.models.product import Product, ProductListing, PriceObservation, Source

DEMO_EMAIL = "demo@priceloop.ai"
DEMO_PASSWORD = "Demo123!"

CATALOG = [
    {
        "name": "Sony WH-1000XM5",
        "brand": "Sony",
        "category": "Audio",
        "base": 348.0,
        "url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        "source": "books_toscrape",
    },
    {
        "name": "Logitech MX Master 3S",
        "brand": "Logitech",
        "category": "Peripherals",
        "base": 95.99,
        "url": "https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html",
        "source": "demo",
    },
    {
        "name": "Apple AirPods Pro 2",
        "brand": "Apple",
        "category": "Audio",
        "base": 249.0,
        "url": "https://example.com/airpods",
        "source": "demo",
    },
]


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == DEMO_EMAIL).first()
        if not user:
            user = User(email=DEMO_EMAIL, hashed_password=hash_password(DEMO_PASSWORD))
            db.add(user)
            db.flush()
            print("created user", DEMO_EMAIL)
        else:
            print("user exists", DEMO_EMAIL)

        for item in CATALOG:
            existing = (
                db.query(Product)
                .filter(Product.user_id == user.id, Product.name == item["name"])
                .first()
            )
            if existing:
                print("skip product", item["name"])
                continue
            src = db.query(Source).filter(Source.name == item["source"]).first()
            if not src:
                src = Source(name=item["source"], base_url=f"https://{item['source']}.example")
                db.add(src)
                db.flush()
            product = Product(
                user_id=user.id,
                name=item["name"],
                brand=item["brand"],
                category=item["category"],
            )
            db.add(product)
            db.flush()
            listing = ProductListing(
                product_id=product.id,
                source_id=src.id,
                external_url=item["url"],
                title=item["name"],
                current_price=Decimal(str(item["base"])),
                currency="USD",
            )
            db.add(listing)
            db.flush()
            # synthetic history
            price = item["base"]
            for days_ago in range(30, 0, -1):
                price = max(1.0, price * (1 + random.uniform(-0.03, 0.03)))
                db.add(
                    PriceObservation(
                        listing_id=listing.id,
                        price=Decimal(str(round(price, 2))),
                        currency="USD",
                        availability="IN_STOCK",
                        scraped_at=datetime.utcnow() - timedelta(days=days_ago),
                    )
                )
            print("seeded", item["name"])
        db.commit()
        print("done. login:", DEMO_EMAIL, DEMO_PASSWORD)
    finally:
        db.close()


if __name__ == "__main__":
    main()
