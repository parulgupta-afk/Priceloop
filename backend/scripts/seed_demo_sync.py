"""
Seed demo user + products using ONLY real books.toscrape.com URLs.

No synthetic brand catalogs (Sony/Amazon/etc.). No invented multi-day
price series. Prices come from a live fetch via the books_toscrape adapter
when the network is available; otherwise listings are stored without
observations and you run scrape later.

Usage (from backend/, DB reachable):

  python -m scripts.seed_demo_sync

Login: demo@priceloop.ai / Demo123!
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent))

from app.core.database import SessionLocal, engine
from app.core.security import hash_password
from app.models.base import Base
from app.models.user import User
from app.models.product import Product, ProductListing, Source
from app.services.scrape_service import scrape_listing

DEMO_EMAIL = "demo@priceloop.ai"
DEMO_PASSWORD = "Demo123!"

# Real product pages on books.toscrape.com (site exists for scraping practice).
# Titles are the published page titles; prices are NOT hard-coded into history —
# they are observed via the adapter when scrape succeeds.
BOOKS_TOSCRAPE_CATALOG = [
    {
        "name": "A Light in the Attic",
        "brand": "Books to Scrape",
        "category": "Poetry",
        "url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
    },
    {
        "name": "Tipping the Velvet",
        "brand": "Books to Scrape",
        "category": "Historical Fiction",
        "url": "https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html",
    },
    {
        "name": "Soumission",
        "brand": "Books to Scrape",
        "category": "Fiction",
        "url": "https://books.toscrape.com/catalogue/soumission_998/index.html",
    },
    {
        "name": "Sharp Objects",
        "brand": "Books to Scrape",
        "category": "Mystery",
        "url": "https://books.toscrape.com/catalogue/sharp-objects_997/index.html",
    },
    {
        "name": "Sapiens: A Brief History of Humankind",
        "brand": "Books to Scrape",
        "category": "History",
        "url": "https://books.toscrape.com/catalogue/sapiens-a-brief-history-of-humankind_996/index.html",
    },
    {
        "name": "The Requiem Red",
        "brand": "Books to Scrape",
        "category": "Young Adult",
        "url": "https://books.toscrape.com/catalogue/the-requiem-red_995/index.html",
    },
    {
        "name": "The Dirty Little Secrets of Getting Your Dream Job",
        "brand": "Books to Scrape",
        "category": "Business",
        "url": "https://books.toscrape.com/catalogue/the-dirty-little-secrets-of-getting-your-dream-job_994/index.html",
    },
    {
        "name": "The Coming Woman: A Novel Based on the Life of the Infamous Feminist Victoria Woodhull",
        "brand": "Books to Scrape",
        "category": "Default",
        "url": "https://books.toscrape.com/catalogue/the-coming-woman-a-novel-based-on-the-life-of-the-infamous-feminist-victoria-woodhull_993/index.html",
    },
]

SOURCE_NAME = "books_toscrape"
SOURCE_BASE = "https://books.toscrape.com"


def main() -> None:
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

        source = db.query(Source).filter(Source.name == SOURCE_NAME).first()
        if not source:
            source = Source(name=SOURCE_NAME, base_url=SOURCE_BASE, is_active=True)
            db.add(source)
            db.flush()
            print("created source", SOURCE_NAME)

        scraped_ok = 0
        scraped_fail = 0

        for item in BOOKS_TOSCRAPE_CATALOG:
            existing = (
                db.query(Product)
                .filter(Product.user_id == user.id, Product.name == item["name"])
                .first()
            )
            if existing:
                print("skip product (already seeded)", item["name"][:60])
                continue

            product = Product(
                user_id=user.id,
                name=item["name"],
                brand=item.get("brand"),
                category=item.get("category"),
            )
            db.add(product)
            db.flush()

            listing = ProductListing(
                product_id=product.id,
                source_id=source.id,
                external_url=item["url"],
                title=item["name"],
                currency="GBP",
            )
            db.add(listing)
            db.flush()
            db.commit()

            # Live observation from the real page (no invented history).
            try:
                obs = scrape_listing(db, listing.id)
                db.commit()
                scraped_ok += 1
                print(
                    f"seeded + scraped  {item['name'][:50]!r}  "
                    f"price={obs.price} {obs.currency}"
                )
            except Exception as exc:
                db.rollback()
                scraped_fail += 1
                print(
                    f"seeded listing only (scrape failed) {item['name'][:50]!r}: "
                    f"{type(exc).__name__}: {exc}"
                )
                print("  -> later: POST /api/listings/<id>/scrape after network is available")

        print()
        print("done.")
        print(f"  login:   {DEMO_EMAIL} / {DEMO_PASSWORD}")
        print(f"  source:  {SOURCE_NAME} only (permitted practice site)")
        print(f"  scraped: {scraped_ok} ok, {scraped_fail} failed")
        print("  history grows only from real scrapes / Celery jobs -- no synthetic series.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
