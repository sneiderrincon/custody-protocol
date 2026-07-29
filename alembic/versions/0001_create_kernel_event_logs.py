"""Create kernel append-only event logs."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_create_kernel_event_logs"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create custody assertion and rejection logs."""

    op.create_table(
        "custody_assertions",
        sa.Column("global_position", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("stream_version", sa.Integer(), nullable=False),
        sa.Column("claim_id", sa.String(length=36), nullable=False),
        sa.Column("unit_id", sa.String(length=255), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("provenance", sa.JSON(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("global_position"),
        sa.UniqueConstraint("claim_id", name="uq_custody_assertions_claim_id"),
        sa.UniqueConstraint("unit_id", "stream_version", name="uq_custody_assertions_stream"),
    )
    op.create_index("ix_custody_assertions_unit_id", "custody_assertions", ["unit_id"])
    op.create_table(
        "rejected_inconsistencies",
        sa.Column("global_position", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("rejection_id", sa.String(length=36), nullable=False),
        sa.Column("attempted_claim_id", sa.String(length=36), nullable=False),
        sa.Column("unit_id", sa.String(length=255), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("reason", sa.String(length=64), nullable=False),
        sa.Column("detail", sa.String(length=2048), nullable=False),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("provenance", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("global_position"),
        sa.UniqueConstraint("rejection_id"),
    )
    op.create_index(
        "ix_rejected_inconsistencies_attempted_claim_id",
        "rejected_inconsistencies",
        ["attempted_claim_id"],
    )
    op.create_index("ix_rejected_inconsistencies_unit_id", "rejected_inconsistencies", ["unit_id"])


def downgrade() -> None:
    """Drop kernel event logs."""

    op.drop_index("ix_rejected_inconsistencies_unit_id", table_name="rejected_inconsistencies")
    op.drop_index(
        "ix_rejected_inconsistencies_attempted_claim_id",
        table_name="rejected_inconsistencies",
    )
    op.drop_table("rejected_inconsistencies")
    op.drop_index("ix_custody_assertions_unit_id", table_name="custody_assertions")
    op.drop_table("custody_assertions")

