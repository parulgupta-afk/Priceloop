"""scrape_jobs and related ops tables

Revision ID: b2c3d4e5f607
Revises: a1b2c3d4e5f6
Create Date: 2026-10-31
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "b2c3d4e5f607"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    tables = set(sa.inspect(bind).get_table_names())
    if "scrape_jobs" not in tables:
        op.create_table(
            "scrape_jobs",
            sa.Column("id", sa.Uuid(), primary_key=True),
            sa.Column("listing_id", sa.Uuid(), sa.ForeignKey("product_listings.id", ondelete="SET NULL"), nullable=True),
            sa.Column("source_name", sa.String(100), nullable=True),
            sa.Column("status", sa.String(32), nullable=False, server_default="PENDING"),
            sa.Column("started_at", sa.DateTime(), nullable=True),
            sa.Column("finished_at", sa.DateTime(), nullable=True),
            sa.Column("duration_ms", sa.Integer(), nullable=True),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        )
        op.create_index("ix_scrape_jobs_listing_id", "scrape_jobs", ["listing_id"])
        op.create_index("ix_scrape_jobs_status", "scrape_jobs", ["status"])

def downgrade() -> None:
    bind = op.get_bind()
    tables = set(sa.inspect(bind).get_table_names())
    if "scrape_jobs" in tables:
        op.drop_table("scrape_jobs")
