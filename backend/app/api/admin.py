from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user, require_roles
from app.models.user import User, UserRole
from app.services.cost_service import cost_summary, record_cost
from app.services.health_service import get_scraper_health
from app.services.self_healing_service import (
    list_proposals,
    mock_ai_suggest_selector,
    propose_selector,
    review_proposal,
)

router = APIRouter(prefix="/admin", tags=["admin"])


class ProposalCreate(BaseModel):
    source_name: str
    field_name: str
    proposed_selector: str
    old_selector: str | None = None
    reason: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)


class CostCreate(BaseModel):
    category: str
    amount: float
    currency: str = "INR"
    source_name: str | None = None
    units: float | None = None


@router.get("/scrapers/health")
async def scraper_health(
    current_user: Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST))],
    db: Annotated[AsyncSession, Depends(get_db)],
    hours: int = Query(24, ge=1, le=168),
):
    return await get_scraper_health(db, hours=hours)


@router.get("/selectors/proposals")
async def get_proposals(
    current_user: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
    status: str | None = Query("PENDING"),
):
    proposals = await list_proposals(db, status=status)
    return [
        {
            "id": str(p.id),
            "source_name": p.source_name,
            "field_name": p.field_name,
            "old_selector": p.old_selector,
            "proposed_selector": p.proposed_selector,
            "reason": p.reason,
            "confidence": p.confidence,
            "status": p.status,
            "created_at": p.created_at.isoformat(),
        }
        for p in proposals
    ]


@router.post("/selectors/proposals", status_code=201)
async def create_proposal(
    body: ProposalCreate,
    current_user: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    p = await propose_selector(
        db,
        source_name=body.source_name,
        field_name=body.field_name,
        proposed_selector=body.proposed_selector,
        old_selector=body.old_selector,
        reason=body.reason,
        confidence=body.confidence,
    )
    return {"id": str(p.id), "status": p.status}


@router.post("/selectors/proposals/{proposal_id}/review")
async def review_selector_proposal(
    proposal_id: UUID,
    approve: bool,
    current_user: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        p = await review_proposal(
            db, proposal_id, approve=approve, reviewer_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {
        "id": str(p.id),
        "status": p.status,
        "reviewed_at": p.reviewed_at.isoformat() if p.reviewed_at else None,
    }


@router.post("/selectors/suggest")
async def ai_suggest(
    source_name: str,
    field_name: str,
    html_snippet: str = "",
    current_user: Annotated[User, Depends(require_roles(UserRole.ADMIN))] = None,
):
    """Demo endpoint: returns a mock AI selector suggestion."""
    suggestion = mock_ai_suggest_selector(html_snippet, field_name)
    return {"source_name": source_name, "field_name": field_name, **suggestion}


@router.get("/costs")
async def get_costs(
    current_user: Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await cost_summary(db)


@router.post("/costs", status_code=201)
async def add_cost(
    body: CostCreate,
    current_user: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    rec = await record_cost(
        db,
        category=body.category,
        amount=body.amount,
        currency=body.currency,
        source_name=body.source_name,
        units=body.units,
    )
    return {"id": str(rec.id), "category": rec.category, "amount": rec.amount}
