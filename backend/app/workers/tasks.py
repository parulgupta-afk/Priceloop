"""Celery tasks for background scraping — sync DB sessions, cooldown to limit duplicates."""
from datetime import datetime, timedelta, timezone
from uuid import UUID
from app.workers.celery_app import celery_app

# Skip re-scrape if last scrape was within this window (seconds)
SCRAPE_COOLDOWN_SECONDS = 300  # 5 minutes


@celery_app.task(name="scrape.listing", bind=True, max_retries=3, default_retry_delay=30)
def scrape_listing_task(self, listing_id: str, force: bool = False) -> dict:
    from app.core.database import SessionLocal
    from app.models.product import ProductListing
    from app.services.scrape_service import scrape_listing
    from app.core.cache import cache_delete_prefix

    db = SessionLocal()
    try:
        listing = db.query(ProductListing).filter(ProductListing.id == UUID(listing_id)).first()
        if listing is None:
            return {"status": "error", "reason": "listing_not_found", "listing_id": listing_id}
        if not force and listing.last_scraped_at is not None:
            age = datetime.now(timezone.utc).replace(tzinfo=None) - listing.last_scraped_at
            if age < timedelta(seconds=SCRAPE_COOLDOWN_SECONDS):
                return {
                    "status": "skipped",
                    "reason": "cooldown",
                    "listing_id": listing_id,
                    "last_scraped_at": listing.last_scraped_at.isoformat(),
                    "cooldown_seconds": SCRAPE_COOLDOWN_SECONDS,
                }
        observation = scrape_listing(db, UUID(listing_id))
        db.commit()
        cache_delete_prefix(f"cache:prices:{listing.product_id}")
        cache_delete_prefix(f"cache:analytics:{listing.product_id}")
        return {
            "status": "success",
            "listing_id": listing_id,
            "observation_id": str(observation.id),
            "price": str(observation.price),
            "currency": observation.currency,
        }
    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc, countdown=30 * (self.request.retries + 1))
    finally:
        db.close()


@celery_app.task(name="scrape.all_active")
def scrape_all_active_task() -> dict:
    from app.core.database import SessionLocal
    from app.models.product import ProductListing

    db = SessionLocal()
    ok, skipped, failed = 0, 0, 0
    try:
        listings = db.query(ProductListing).filter(ProductListing.is_active.is_(True)).all()
        for listing in listings:
            try:
                result = scrape_listing_task.apply(args=[str(listing.id)], throw=True)
                # apply() returns EagerResult in some modes; handle dict
                payload = result if isinstance(result, dict) else (getattr(result, "result", None) or {})
                st = payload.get("status") if isinstance(payload, dict) else None
                if st == "success":
                    ok += 1
                elif st == "skipped":
                    skipped += 1
                else:
                    # enqueue async for true worker parallelism when called from beat
                    scrape_listing_task.delay(str(listing.id))
                    ok += 1
            except Exception:
                failed += 1
        return {"status": "done", "success": ok, "skipped": skipped, "failed": failed, "total": len(listings)}
    finally:
        db.close()
