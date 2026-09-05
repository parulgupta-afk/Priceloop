"""
Periodic task definitions (Celery Beat).
In production you would run:
  celery -A app.workers.celery_app beat --loglevel=info
"""

from celery.schedules import crontab

from app.workers.celery_app import celery_app

# Example schedule – adjust later per product frequency
celery_app.conf.beat_schedule = {
    # Every hour: scrape all active listings (demo scale)
    "scrape-all-active-listings-hourly": {
        "task": "scrape.all_active",
        "schedule": crontab(minute=0),  # top of every hour
    },
}

celery_app.conf.timezone = "UTC"
