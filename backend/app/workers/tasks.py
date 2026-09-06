"""Celery tasks for background scraping — sync DB sessions."""

from uuid import UUID

from app.workers.celery_app import celery_app


@celery_app.task(name="scrape.listing", bind=True, max_retries=3)
def scrape_listing_task(self, listing_id: str) -> dict:
    from app.core.database import SessionLocal
    from app.services.scrape_service import scrape_listing

    db = SessionLocal()
    try:
        observation = scrape_listing(db, UUID(listing_id))
        db.commit()
        return {
            "status": "success",
            "listing_id": listing_id,
            "observation_id": str(observation.id),
            "price": str(observation.price),
            "currency": observation.currency,
        }
    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc, countdown=30)
    finally:
        db.close()


@celery_app.task(name="scrape.all_active")
def scrape_all_active_task() -> dict:
    from app.core.database import SessionLocal
    from app.models.product import ProductListing
    from app.services.scrape_service import scrape_listing

    db = SessionLocal()
    ok, failed = 0, 0
    try:
        listings = (
            db.query(ProductListing)
            .filter(ProductListing.is_active.is_(True))
            .all()
        )
        for listing in listings:
            try:
                scrape_listing(db, listing.id)
                db.commit()
                ok += 1
            except Exception:
                db.rollback()
                failed += 1
        return {"status": "done", "success": ok, "failed": failed, "total": len(listings)}
    finally:
        db.close()
