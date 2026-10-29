"""price observations, sources, history indexes

Revision ID: a1b2c3d4e5f6
Revises: d2289b79d558
Create Date: 2026-10-29
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "d2289b79d558"
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    if "sources" not in tables:
        op.create_table(
            "sources",
            sa.Column("id", sa.Uuid(), nullable=False),
            sa.Column("name", sa.String(100), nullable=False),
            sa.Column("base_url", sa.String(500), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
            sa.Column("rate_limit_per_second", sa.Numeric(5, 2), nullable=False, server_default="1.0"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("name"),
        )
    if "price_observations" not in tables:
        op.create_table(
            "price_observations",
            sa.Column("id", sa.Uuid(), nullable=False),
            sa.Column("listing_id", sa.Uuid(), nullable=False),
            sa.Column("price", sa.Numeric(12, 2), nullable=False),
            sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
            sa.Column("availability", sa.String(12), nullable=False, server_default="IN_STOCK"),
            sa.Column("scraped_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("raw_data", sa.JSON(), nullable=True),
            sa.ForeignKeyConstraint(["listing_id"], ["product_listings.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    try:
        op.create_index("idx_price_observation_history", "price_observations", ["listing_id", sa.text("scraped_at DESC")])
    except Exception:
        pass
    try:
        op.create_index("idx_price_observation_scraped_at", "price_observations", ["scraped_at"])
    except Exception:
        pass

def downgrade() -> None:
    try:
        op.drop_index("idx_price_observation_scraped_at", table_name="price_observations")
    except Exception:
        pass
    try:
        op.drop_index("idx_price_observation_history", table_name="price_observations")
    except Exception:
        pass
    bind = op.get_bind()
    tables = set(sa.inspect(bind).get_table_names())
    if "price_observations" in tables:
        op.drop_table("price_observations")
    if "sources" in tables:
        op.drop_table("sources")
