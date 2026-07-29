"""Rejected inconsistency domain event."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from kernel.custody.domain.events import CustodyEventType, RejectionReason
from kernel.custody.domain.value_objects import Provenance


class RejectedInconsistency(BaseModel):
    """Append-only event for a rejected custody assertion attempt."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    rejection_id: UUID
    attempted_claim_id: UUID
    unit_id: str = Field(min_length=1)
    event_type: CustodyEventType
    reason: RejectionReason
    detail: str = Field(min_length=1)
    rejected_at: datetime
    provenance: Provenance

    @field_validator("rejected_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        """Normalize rejected-at timestamps to UTC."""

        if value.tzinfo is None:
            msg = "rejected_at must be timezone-aware"
            raise ValueError(msg)
        return value.astimezone(UTC)

