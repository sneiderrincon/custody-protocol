"""Custody write commands."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from kernel.custody.domain.events import CustodyEventType
from kernel.custody.domain.value_objects import AssertionPayload, Provenance


class DeclareCustodyAssertion(BaseModel):
    """Command for the single conceptual write API."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    claim_id: UUID
    unit_id: str = Field(min_length=1)
    event_type: CustodyEventType
    occurred_at: datetime
    provenance: Provenance
    payload: AssertionPayload = Field(default_factory=AssertionPayload)

