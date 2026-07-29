"""Custody value objects."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

PayloadScalar = str | int | float | bool | None


class EvidenceReference(BaseModel):
    """A verifiable pointer to evidence held outside the custody log."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    uri: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[a-fA-F0-9]{64}$")


class Provenance(BaseModel):
    """Origin metadata for a custody assertion."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    actor_id: UUID
    adapter_id: str = Field(min_length=1)
    declared_at: datetime
    evidence: tuple[EvidenceReference, ...] = ()

    @field_validator("declared_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            msg = "declared_at must be timezone-aware"
            raise ValueError(msg)
        return value.astimezone(UTC)


class PayloadAttribute(BaseModel):
    """Immutable adapter metadata attribute."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    key: str = Field(min_length=1)
    value: PayloadScalar


class AssertionPayload(BaseModel):
    """Opaque immutable metadata for an event type.

    The kernel accepts structured metadata but never derives truth from arbitrary adapter
    fields. Domain rules must use explicit event vocabulary and provenance.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    attributes: tuple[PayloadAttribute, ...] = ()
