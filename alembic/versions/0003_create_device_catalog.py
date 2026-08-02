"""Create device catalog table."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_create_device_catalog"
down_revision: str | None = "0002_enforce_append_only_immutability"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the canonical device catalog table."""

    op.create_table(
        "catalog_devices",
        sa.Column("device_id", sa.String(length=36), nullable=False),
        sa.Column("udi_di_value", sa.String(length=255), nullable=False),
        sa.Column("udi_di_issuing_agency", sa.String(length=16), nullable=False),
        sa.Column("generic_regulatory_name", sa.String(length=512), nullable=False),
        sa.Column("manufacturer", sa.JSON(), nullable=False),
        sa.Column("manufacturer_model_reference", sa.String(length=255), nullable=False),
        sa.Column("gmdn", sa.JSON(), nullable=False),
        sa.Column("risk_class", sa.String(length=8), nullable=False),
        sa.Column("regulatory_registrations", sa.JSON(), nullable=False),
        sa.Column("packaging", sa.JSON(), nullable=False),
        sa.Column("unit_of_measure", sa.String(length=64), nullable=False),
        sa.Column("minimum_consumption_unit", sa.String(length=64), nullable=False),
        sa.Column("storage_conditions", sa.JSON(), nullable=False),
        sa.Column("sterilization", sa.JSON(), nullable=False),
        sa.Column("commercial_presentation", sa.String(length=512), nullable=False),
        sa.Column("lifecycle_status", sa.String(length=16), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("device_id"),
        sa.UniqueConstraint("udi_di_value", name="uq_catalog_devices_udi_di"),
    )
    op.create_index("ix_catalog_devices_udi_di_value", "catalog_devices", ["udi_di_value"])


def downgrade() -> None:
    """Drop the canonical device catalog table."""

    op.drop_table("catalog_devices")
