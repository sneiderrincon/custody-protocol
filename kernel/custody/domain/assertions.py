"""Custody assertion entities."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from kernel.custody.domain.events import CustodyEventType
from kernel.custody.domain.value_objects import AssertionPayload, Provenance


class CustodyAssertionDraft(BaseModel):
    """Uncommitted assertion proposed by an actor through an adapter."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    claim_id: UUID
    unit_id: str = Field(min_length=1)
    event_type: CustodyEventType
    occurred_at: datetime
    provenance: Provenance
    payload: AssertionPayload = Field(default_factory=AssertionPayload)

    @field_validator("occurred_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            msg = "occurred_at must be timezone-aware"
            raise ValueError(msg)
        return value.astimezone(UTC)


class CommittedCustodyAssertion(CustodyAssertionDraft):
    """Immutable custody assertion appended to the event store."""

    global_position: int = Field(ge=1)
    stream_version: int = Field(ge=1)

    def matches_draft(self, draft: CustodyAssertionDraft) -> bool:
        """Return whether this committed assertion has the same content as ``draft``.

        Used by event-store adapters to resolve idempotent replays: two
        assertions match when everything but their store-assigned positions
        is identical.
        """

        committed_content = self.model_dump(exclude={"global_position", "stream_version"})
        return committed_content == draft.model_dump()


