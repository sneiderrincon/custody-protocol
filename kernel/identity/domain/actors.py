"""Identity domain model for institutional actors."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ActorStatus(StrEnum):
    """Lifecycle status for an institutional actor."""

    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    RETIRED = "retired"


class TrustLevel(StrEnum):
    """Governance trust tier assigned to an actor credential."""

    LOW = "low"
    STANDARD = "standard"
    HIGH = "high"


class Actor(BaseModel):
    """Institutional participant allowed to make verifiable claims."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    actor_id: UUID
    legal_name: str = Field(min_length=1)
    status: ActorStatus
    trust_level: TrustLevel

    @property
    def can_declare_claims(self) -> bool:
        """Return whether the actor may submit custody claims."""

        return self.status == ActorStatus.ACTIVE

