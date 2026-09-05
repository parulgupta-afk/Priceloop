"""
Orchestrates scraping a ProductListing and storing a PriceObservation.
Uses the scraper package adapters.
"""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import AvailabilityStatus, PriceObservation, ProductListing, Source
from app.services.normalization import normalize_availability, normalize_price, normalize_title

# Import demo scraper – later this will be a registry
import sys
from pathlib import Path

# Monorepo root (…/Priceloop) and /app fallbacks for Docker
_here = Path(__file__).resolve()
for candidate in (
    _here.parents[3],           # repo root when running from backend/app/services
    _here.parents[2],           # backend/ when structure differs
    Path('/app'),
    Path('/app/..').resolve(),
):
    if (candidate / 'scraper').is_dir() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

try:
    from scraper.adapters.demo import DemoScraper  # noqa: E402
    from scraper.core.base import BaseScraper  # noqa: E402
except ModuleNotFoundError:
    # Minimal inline fallback so API still boots without scraper package
    class BaseScraper:  # type: ignore
        def scrape(self, url: str):
            return {"title": "Unavailable", "price": None, "currency": "USD", "availability": "UNKNOWN"}

    class DemoScraper(BaseScraper):  # type: ignore
        def scrape(self, url: str):
            return {
                "title": "Demo listing",
                "price": 99.0,
                "currency": "USD",
                "availability": "IN_STOCK",
            }


ADAPTER_REGISTRY: dict[str, type[BaseScraper]] = {
    "demo": DemoScraper,
}


def get_adapter(source_name: str) -> BaseScraper:
    key = source_name.lower().strip()
    cls = ADAPTER_REGISTRY.get(key)
    if cls is None:
        # Fallback to demo for development
        cls = DemoScraper
    return cls()


async def scrape_listing(db: AsyncSession, listing_id: UUID) -> PriceObservation:
    """
    Fetch the listing, run the appropriate adapter, normalize, and persist.
    """
    result = await db.execute(
        select(ProductListing)
        .where(ProductListing.id == listing_id)
        .join(Source)
    )
    listing = result.scalar_one_or_none()
    if listing is None:
        raise ValueError(f"Listing {listing_id} not found")

    # Load source name
    source_result = await db.execute(select(Source).where(Source.id == listing.source_id))
    source = source_result.scalar_one()

    adapter = get_adapter(source.name)
    scraped = await adapter.scrape(listing.external_url)

    price, currency = normalize_price(scraped.price)
    if price is None and scraped.price is not None:
        # already a Decimal from the adapter
        try:
            price = Decimal(str(scraped.price))
            currency = scraped.currency or "INR"
        except Exception:
            price = None

    availability = normalize_availability(scraped.availability)
    title = normalize_title(scraped.title)

    # Update listing snapshot
    if price is not None:
        listing.current_price = price
        listing.currency = currency
    listing.availability = AvailabilityStatus(availability)
    if title:
        listing.title = title
    listing.last_scraped_at = datetime.now(timezone.utc)

    # Create observation
    observation = PriceObservation(
        listing_id=listing.id,
        price=price or Decimal("0"),
        currency=currency,
        availability=AvailabilityStatus(availability),
        scraped_at=datetime.now(timezone.utc),
        raw_data={
            "title": scraped.title,
            "rating": scraped.rating,
            "review_count": scraped.review_count,
            "seller": scraped.seller,
            "adapter": adapter.name,
        },
    )
    db.add(observation)
    await db.flush()
    await db.refresh(observation)

    # Observability: record a successful scrape job
    try:
        from app.models.scraper_ops import ScrapeJobStatus
        from app.services.health_service import record_job

        await record_job(
            db,
            listing_id=listing.id,
            source_name=source.name,
            status=ScrapeJobStatus.SUCCESS,
            duration_ms=50,  # demo value; real adapter can measure
        )
    except Exception:
        pass  # never fail the main scrape path because of metrics

    return observation
