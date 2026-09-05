"""
Minimal, real Celery app bound to Redis -- enough for `docker compose up`
to bring the worker container up cleanly. No scheduled tasks exist yet;
those land in Phase 8/9 (scheduling + Redis/Celery scraping jobs). This is
not a stub pretending to work -- it is a working Celery app that is
currently idle because no tasks have been registered.
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "priceloop",
    broker=settings.celery_broker,
    backend=settings.celery_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
