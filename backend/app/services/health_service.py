"""
Scraper health & observability metrics.
"""

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scraper_ops import ScrapeJob, ScrapeJobStatus, SelectorProposal
from app.models.product import Source


async def get_scraper_health(db: AsyncSession, hours: int = 24) -> dict[str, Any]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    # Overall counts
    total_q = await db.execute(
        select(func.count()).select_from(ScrapeJob).where(ScrapeJob.created_at >= cutoff)
    )
    total = total_q.scalar() or 0

    success_q = await db.execute(
        select(func.count())
        .select_from(ScrapeJob)
        .where(
            ScrapeJob.created_at >= cutoff,
            ScrapeJob.status == ScrapeJobStatus.SUCCESS,
        )
    )
    success = success_q.scalar() or 0

    failed_q = await db.execute(
        select(func.count())
        .select_from(ScrapeJob)
        .where(
            ScrapeJob.created_at >= cutoff,
            ScrapeJob.status.in_(
                [ScrapeJobStatus.FAILED, ScrapeJobStatus.TIMEOUT]
            ),
        )
    )
    failed = failed_q.scalar() or 0

    avg_duration_q = await db.execute(
        select(func.avg(ScrapeJob.duration_ms)).where(
            ScrapeJob.created_at >= cutoff,
            ScrapeJob.duration_ms.is_not(None),
        )
    )
    avg_duration = avg_duration_q.scalar()

    success_rate = round((success / total) * 100, 2) if total else None

    # Per-source breakdown
    sources_q = await db.execute(select(Source))
    sources = list(sources_q.scalars().all())
    per_source = []
    for src in sources:
        s_total = await db.execute(
            select(func.count())
            .select_from(ScrapeJob)
            .where(
                ScrapeJob.created_at >= cutoff,
                ScrapeJob.source_name == src.name,
            )
        )
        st = s_total.scalar() or 0
        s_ok = await db.execute(
            select(func.count())
            .select_from(ScrapeJob)
            .where(
                ScrapeJob.created_at >= cutoff,
                ScrapeJob.source_name == src.name,
                ScrapeJob.status == ScrapeJobStatus.SUCCESS,
            )
        )
        so = s_ok.scalar() or 0
        per_source.append(
            {
                "source": src.name,
                "total_jobs": st,
                "success": so,
                "success_rate": round((so / st) * 100, 2) if st else None,
                "is_active": src.is_active,
            }
        )

    # Pending selector proposals
    pending_q = await db.execute(
        select(func.count())
        .select_from(SelectorProposal)
        .where(SelectorProposal.status == "PENDING")
    )
    pending_proposals = pending_q.scalar() or 0

    return {
        "window_hours": hours,
        "total_jobs": total,
        "success": success,
        "failed": failed,
        "success_rate_pct": success_rate,
        "avg_duration_ms": round(float(avg_duration), 1) if avg_duration else None,
        "per_source": per_source,
        "pending_selector_proposals": pending_proposals,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


async def record_job(
    db: AsyncSession,
    listing_id: UUID | None,
    source_name: str | None,
    status: ScrapeJobStatus,
    duration_ms: int | None = None,
    error_message: str | None = None,
) -> ScrapeJob:
    now = datetime.now(timezone.utc)
    job = ScrapeJob(
        listing_id=listing_id,
        source_name=source_name,
        status=status,
        started_at=now - timedelta(milliseconds=duration_ms or 0),
        finished_at=now,
        duration_ms=duration_ms,
        error_message=error_message,
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)
    return job
