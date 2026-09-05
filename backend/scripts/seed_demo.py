"""
Seed a demo user + catalog of products with multi-source listings and price history.

Usage (from backend/ with venv active and Postgres up):

  python -m scripts.seed_demo
"""

from __future__ import annotations

import asyncio
import random
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent))

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.product import (
    AvailabilityStatus,
    PriceObservation,
    Product,
    ProductListing,
    Source,
)

CATALOG = [
    {
        "name": "Sony WH-1000XM5",
        "brand": "Sony",
        "model": "WH-1000XM5",
        "category": "Audio",
        "sku": "SNY-WH-XM5-BLK",
        "description": "Wireless Noise Canceling Headphones",
        "image_url": "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=400&h=400&fit=crop",
        "base_price": 348.0,
        "sources": [
            ("amazon", "https://www.amazon.com/dp/B09XS7JWHH", 348.0),
            ("bestbuy", "https://www.bestbuy.com/site/sony-wh-1000xm5/6505727.p", 349.99),
            ("walmart", "https://www.walmart.com/ip/sony-wh1000xm5", 355.0),
        ],
    },
    {
        "name": "Logitech MX Master 3S",
        "brand": "Logitech",
        "model": "MX Master 3S",
        "category": "Peripherals",
        "sku": "LOG-MX-M3S-GRY",
        "description": "Performance Wireless Ergonomic Mouse",
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400&h=400&fit=crop",
        "base_price": 95.99,
        "sources": [
            ("amazon", "https://www.amazon.com/dp/B09HM94VDS", 95.99),
            ("bestbuy", "https://www.bestbuy.com/site/logitech-mx-master-3s/6505070.p", 99.99),
        ],
    },
    {
        "name": "Keychron K8 Pro",
        "brand": "Keychron",
        "model": "K8 Pro",
        "category": "Peripherals",
        "sku": "KEY-K8P-RGB-RED",
        "description": "Wireless Mechanical Keyboard",
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400&h=400&fit=crop",
        "base_price": 109.0,
        "sources": [
            ("amazon", "https://www.amazon.com/dp/B0B1XXXXX", 109.0),
            ("target", "https://www.target.com/p/keychron-k8-pro/-/A-123", 114.99),
        ],
    },
    {
        "name": "LG 32UN880-B 4K Monitor",
        "brand": "LG",
        "model": "32UN880-B",
        "category": "Displays",
        "sku": "MON-32-UHD-4K",
        "description": "32-inch 4K Ergo IPS Monitor",
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=400&h=400&fit=crop",
        "base_price": 549.0,
        "sources": [
            ("amazon", "https://www.amazon.com/dp/B08XXXX", 549.0),
            ("bestbuy", "https://www.bestbuy.com/site/lg-32un880/6400000.p", 579.99),
            ("walmart", "https://www.walmart.com/ip/lg-32un880", 559.0),
        ],
    },
    {
        "name": "Herman Miller Aeron",
        "brand": "Herman Miller",
        "model": "Aeron Remastered",
        "category": "Furniture",
        "sku": "CHR-ERG-PRO-BLK",
        "description": "Ergonomic Office Chair Size B",
        "image_url": "https://images.unsplash.com/photo-1580480055273-228ff5388ef8?w=400&h=400&fit=crop",
        "base_price": 1395.0,
        "sources": [
            ("amazon", "https://www.amazon.com/dp/B07XXXX", 1395.0),
            ("target", "https://www.target.com/p/aeron/-/A-456", 1495.0),
        ],
    },
]



async def ensure_source(db, name: str, base_url: str) -> Source:
    result = await db.execute(select(Source).where(Source.name == name))
    source = result.scalar_one_or_none()
    if not source:
        source = Source(name=name, base_url=base_url)
        db.add(source)
        await db.flush()
    return source


async def seed_price_history(
    db,
    listing_id,
    start_price: float,
    days: int = 30,
) -> int:
    """Insert synthetic but realistic daily price points (idempotent-ish)."""
    existing = await db.execute(
        select(PriceObservation).where(PriceObservation.listing_id == listing_id).limit(1)
    )
    if existing.scalar_one_or_none():
        return 0

    now = datetime.now(timezone.utc)
    price = float(start_price)
    count = 0
    for d in range(days, -1, -1):
        # small random walk
        price = max(1.0, price * (1 + random.uniform(-0.02, 0.02)))
        obs = PriceObservation(
            listing_id=listing_id,
            price=Decimal(str(round(price, 2))),
            currency="USD",
            availability=AvailabilityStatus.IN_STOCK,
            scraped_at=now - timedelta(days=d, hours=random.randint(0, 12)),
        )
        db.add(obs)
        count += 1
    return count


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # User
        result = await db.execute(select(User).where(User.email == "demo@priceloop.local"))
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                email="demo@priceloop.local",
                hashed_password=get_password_hash("demo12345"),
                full_name="Demo User",
                role=UserRole.ADMIN,
                is_verified=True,
            )
            db.add(user)
            await db.flush()
            print("Created user: demo@priceloop.local / demo12345")
        else:
            print("User already exists: demo@priceloop.local")

        source_urls = {
            "amazon": "https://www.amazon.com",
            "bestbuy": "https://www.bestbuy.com",
            "walmart": "https://www.walmart.com",
            "target": "https://www.target.com",
            "demo": "https://demo.priceloop.local",
        }
        sources: dict[str, Source] = {}
        for name, url in source_urls.items():
            sources[name] = await ensure_source(db, name, url)

        total_obs = 0
        for item in CATALOG:
            prod_result = await db.execute(
                select(Product).where(
                    Product.user_id == user.id,
                    Product.sku == item["sku"],
                )
            )
            product = prod_result.scalar_one_or_none()
            if not product:
                product = Product(
                    user_id=user.id,
                    name=item["name"],
                    brand=item["brand"],
                    model=item["model"],
                    category=item["category"],
                    sku=item["sku"],
                    description=item["description"],
                    image_url=item["image_url"],
                    attributes={"cogs": round(item["base_price"] * 0.72, 2)},
                )
                db.add(product)
                await db.flush()
                print(f"Created product: {item['name']}")
            else:
                # Keep images fresh on re-seed
                if item.get("image_url") and product.image_url != item["image_url"]:
                    product.image_url = item["image_url"]
                    print(f"Updated image: {item['name']}")
                else:
                    print(f"Product exists: {item['name']}")

            for src_name, ext_url, price in item["sources"]:
                list_result = await db.execute(
                    select(ProductListing).where(
                        ProductListing.product_id == product.id,
                        ProductListing.external_url == ext_url,
                    )
                )
                listing = list_result.scalar_one_or_none()
                if not listing:
                    listing = ProductListing(
                        product_id=product.id,
                        source_id=sources[src_name].id,
                        external_url=ext_url,
                        external_id=None,
                        title=f"{item['name']} @ {src_name}",
                        current_price=Decimal(str(price)),
                        currency="USD",
                        availability=AvailabilityStatus.IN_STOCK,
                        last_scraped_at=datetime.now(timezone.utc),
                        is_active=True,
                    )
                    db.add(listing)
                    await db.flush()
                    print(f"  + listing {src_name} @ ${price}")
                total_obs += await seed_price_history(db, listing.id, float(price), days=30)

        await db.commit()
        print(f"Done. Price observations inserted this run: {total_obs}")
        print("Login: demo@priceloop.local / demo12345")


if __name__ == "__main__":
    asyncio.run(main())
