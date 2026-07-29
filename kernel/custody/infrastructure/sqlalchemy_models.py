"""SQLAlchemy mappings for custody persistence."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from kernel.shared.infrastructure.database import Base


class CustodyAssertionRecord(Base):
    """ORM row for an immutable custody assertion."""

    __tablename__ = "custody_assertions"
    __table_args__ = (
        UniqueConstraint("claim_id", name="uq_custody_assertions_claim_id"),
        UniqueConstraint("unit_id", "stream_version", name="uq_custody_assertions_stream"),
    )

    global_position: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stream_version: Mapped[int] = mapped_column(Integer, nullable=False)
    claim_id: Mapped[str] = mapped_column(String(36), nullable=False)
    unit_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    provenance: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)


class RejectedInconsistencyRecord(Base):
    """ORM row for an immutable rejected inconsistency event."""

    __tablename__ = "rejected_inconsistencies"

    global_position: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rejection_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True)
    attempted_claim_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    unit_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    reason: Mapped[str] = mapped_column(String(64), nullable=False)
    detail: Mapped[str] = mapped_column(String(2048), nullable=False)
    rejected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    provenance: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
