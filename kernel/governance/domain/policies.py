"""Governance policies for custody write authorization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from kernel.custody.domain.assertions import CustodyAssertionDraft
from kernel.shared.domain.errors import DomainError


class GovernancePolicyViolationError(DomainError):
    """Raised when a claim violates governance policy."""


class AuthorizableActor(Protocol):
    """The only actor shape governance needs, decoupled from identity's domain.

    Any object with these two members satisfies this protocol structurally,
    so governance never has to import the identity bounded context's model.
    """

    actor_id: UUID

    @property
    def can_declare_claims(self) -> bool: ...


@dataclass(frozen=True, slots=True)
class CustodyDeclarationPolicy:
    """Policy that decides whether an actor may declare a custody claim."""

    policy_version: str = "governance/custody-declaration/v1"

    def authorize(self, actor: AuthorizableActor | None, draft: CustodyAssertionDraft) -> None:
        """Validate that the draft provenance is allowed to enter Custody."""

        if actor is None:
            msg = f"unknown actor {draft.provenance.actor_id}"
            raise GovernancePolicyViolationError(msg)
        if not actor.can_declare_claims:
            msg = f"actor {actor.actor_id} cannot declare custody claims"
            raise GovernancePolicyViolationError(msg)

