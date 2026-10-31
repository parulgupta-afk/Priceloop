"""
Orchestrates scraping a ProductListing and storing a PriceObservation.
Records ScrapeJob rows for observability (Phase 2).
"""
from __future__ import annotations

import sys
import time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.product import AvailabilityStatus, PriceObservation, ProductListing, Source
from app.services.normalization import normalize_availability, normalize_price, normalize_title

_here = Path(__file__).resolve()
for candidate in (
    _here.parents[3],
    _here.parents[2],
    Path("/app"),
    Path("/app/..").resolve(),
):
    if (candidate / "scraper").is_dir() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

try:
    from scraper.adapters.demo import DemoScraper  # noqa: E402
    from scraper.core.base import BaseScraper  # noqa: E402
except ModuleNotFoundError:

    class BaseScraper:  # type: ignore
        def scrape(self, url: str):
            return {"title": "Unavailable", "price": None, "currency": "USD", "availability": "UNKNOWN"}

    class DemoScraper(BaseScraper):  # type: ignore
        def scrape(self, url: str):
            return {"title": "Demo listing", "price": 99.0, "currency": "USD", "availability": "IN_STOCK"}


def _load_books_adapter():
    try:
        from scraper.adapters.books_toscrape import BooksToScrapeAdapter

        class BooksToScrapeCompat(BaseScraper):  # type: ignore
            def scrape(self, url: str):
                adapter = BooksToScrapeAdapter()
                raw = adapter.fetch(url)
                data = adapter.parse(raw)
                return {
                    "title": data.title,
                    "price": data.price,
                    "currency": data.currency or "GBP",
                    "availability": data.availability or "UNKNOWN",
                    "source": "books_toscrape",
                }

        return BooksToScrapeCompat
    except Exception:
        return None


ADAPTER_REGISTRY: dict[str, type] = {"demo": DemoScraper}
_books = _load_books_adapter()
if _books is not None:
    ADAPTER_REGISTRY["books_toscrape"] = _books
    ADAPTER_REGISTRY["books"] = _books


def get_adapter(source_name: str):
    key = (source_name or "demo").lower().strip()
    cls = ADAPTER_REGISTRY.get(key, DemoScraper)
    return cls()


def _record_job(db: Session, listing_id, source_name: str, status: str, error=None, duration_ms=None):
    try:
        from app.models.scraper_ops import ScrapeJob, ScrapeJobStatus

        st = ScrapeJobStatus[status] if status in ScrapeJobStatus.__members__ else ScrapeJobStatus.FAILED
        job = ScrapeJob(
            listing_id=listing_id,
            source_name=source_name,
            status=st,
            started_at=datetime.now(timezone.utc).replace(tzinfo=None) if status == "RUNNING" else None,
            finished_at=datetime.now(timezone.utc).replace(tzinfo=None)
            if status in ("SUCCESS", "FAILED", "TIMEOUT")
            else None,
            duration_ms=duration_ms,
            error_message=(str(error)[:2000] if error else None),
        )
        db.add(job)
        db.flush()
        return job
    except Exception:
        return None


def scrape_listing(db: Session, listing_id: UUID) -> PriceObservation:
    listing = db.query(ProductListing).filter(ProductListing.id == listing_id).first()
    if listing is None:
        raise ValueError(f"Listing {listing_id} not found")

    source_name = "demo"
    if listing.source_id:
        source = db.query(Source).filter(Source.id == listing.source_id).first()
        if source:
            source_name = source.name

    adapter = get_adapter(source_name)
    t0 = time.perf_counter()
    _record_job(db, listing.id, source_name, "RUNNING")

    try:
        try:
            from app.core.resilience import retry_with_backoff

            raw = retry_with_backoff(
                lambda: adapter.scrape(listing.external_url) or {},
                max_attempts=3,
                base_delay=0.4,
            )
        except ImportError:
            raw = adapter.scrape(listing.external_url) or {}

        title = normalize_title(raw.get("title") or listing.title or "")
        price_val, detected_currency = normalize_price(raw.get("price"))
        currency = (raw.get("currency") or detected_currency or listing.currency or "USD")[:3].upper()
        availability = normalize_availability(raw.get("availability")) or AvailabilityStatus.UNKNOWN.value

        if price_val is None:
            raise ValueError(f"No price returned for listing {listing_id}")

        obs = PriceObservation(
            listing_id=listing.id,
            price=Decimal(str(price_val)),
            currency=currency,
            availability=str(availability),
            scraped_at=datetime.now(timezone.utc).replace(tzinfo=None),
            raw_data=raw if isinstance(raw, dict) else {"raw": str(raw)},
        )
        db.add(obs)

        listing.current_price = obs.price
        listing.currency = currency
        listing.availability = obs.availability
        listing.last_scraped_at = obs.scraped_at
        if title:
            listing.title = title

        duration_ms = int((time.perf_counter() - t0) * 1000)
        _record_job(db, listing.id, source_name, "SUCCESS", duration_ms=duration_ms)
        db.flush()
        return obs
    except Exception as exc:
        duration_ms = int((time.perf_counter() - t0) * 1000)
        _record_job(db, listing.id, source_name, "FAILED", error=exc, duration_ms=duration_ms)
        raise
