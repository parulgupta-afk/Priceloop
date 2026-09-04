import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ScrapeJobStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"


class ScrapeJob(Base):
    __tablename__ = "scrape_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    listing_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("product_listings.id", ondelete="SET NULL"), index=True
    )
    source_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[ScrapeJobStatus] = mapped_column(
        Enum(ScrapeJobStatus), default=ScrapeJobStatus.PENDING, index=True
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ScrapeResult(Base):
    __tablename__ = "scrape_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scrape_jobs.id", ondelete="CASCADE"), index=True
    )
    success: Mapped[bool] = mapped_column(Boolean, default=False)
    extracted_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    raw_html_snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    screenshot_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class SelectorProposal(Base):
    """
    Self-healing: when extraction fails repeatedly, the system can propose
    a new CSS/XPath selector. Human approval is required before activation.
    """

    __tablename__ = "selector_proposals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_name: Mapped[str] = mapped_column(String(100), index=True)
    field_name: Mapped[str] = mapped_column(String(50))  # price, title, availability...
    old_selector: Mapped[str | None] = mapped_column(Text, nullable=True)
    proposed_selector: Mapped[str] = mapped_column(Text, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="PENDING"
    )  # PENDING / APPROVED / REJECTED
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)


class CostRecord(Base):
    __tablename__ = "cost_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    category: Mapped[str] = mapped_column(String(50))  # scraping, proxy, ai, database, compute
    source_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)  # in INR or USD
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    units: Mapped[float | None] = mapped_column(Float, nullable=True)  # requests, tokens, etc.
    period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
