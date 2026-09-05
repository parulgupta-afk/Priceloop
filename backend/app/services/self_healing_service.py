"""
Self-healing selector proposals.
When extraction starts failing, the system can suggest a new selector.
IMPORTANT: proposals stay PENDING until a human approves them.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scraper_ops import SelectorProposal


async def propose_selector(
    db: AsyncSession,
    source_name: str,
    field_name: str,
    proposed_selector: str,
    old_selector: str | None = None,
    reason: str | None = None,
    confidence: float | None = None,
) -> SelectorProposal:
    proposal = SelectorProposal(
        source_name=source_name.lower(),
        field_name=field_name,
        old_selector=old_selector,
        proposed_selector=proposed_selector,
        reason=reason or "Automated suggestion after repeated extraction failures",
        confidence=confidence,
        status="PENDING",
    )
    db.add(proposal)
    await db.flush()
    await db.refresh(proposal)
    return proposal


async def list_proposals(
    db: AsyncSession, status: str | None = "PENDING"
) -> list[SelectorProposal]:
    q = select(SelectorProposal).order_by(SelectorProposal.created_at.desc())
    if status:
        q = q.where(SelectorProposal.status == status)
    result = await db.execute(q)
    return list(result.scalars().all())


async def review_proposal(
    db: AsyncSession,
    proposal_id: UUID,
    approve: bool,
    reviewer_id: UUID | None = None,
) -> SelectorProposal:
    result = await db.execute(
        select(SelectorProposal).where(SelectorProposal.id == proposal_id)
    )
    proposal = result.scalar_one_or_none()
    if not proposal:
        raise ValueError("Proposal not found")

    proposal.status = "APPROVED" if approve else "REJECTED"
    proposal.reviewed_at = datetime.now(timezone.utc)
    proposal.reviewed_by = reviewer_id
    await db.flush()
    await db.refresh(proposal)

    # NOTE: In a full implementation, APPROVED would update the live
    # adapter configuration / selector store after running fixture tests.
    # We deliberately keep that step explicit and human-gated.

    return proposal


def mock_ai_suggest_selector(html_snippet: str, field_name: str) -> dict[str, Any]:
    """
    Placeholder for an LLM that inspects HTML and suggests a selector.
    Returns a conservative mock so the pipeline is demonstrable offline.
    """
    suggestions = {
        "price": ".price, [data-price], .a-price-whole",
        "title": "h1, #product-title, .product-title",
        "availability": ".availability, #availability, .stock",
    }
    return {
        "proposed_selector": suggestions.get(field_name, f".{field_name}"),
        "confidence": 0.72,
        "reason": f"Mock AI suggestion for field '{field_name}' based on common patterns.",
    }
