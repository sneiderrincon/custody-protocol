"""Governance policies for custody write authorization."""

from __future__ import annotations

from dataclasses import dataclass

from kernel.custody.domain.assertions import CustodyAssertionDraft
from kernel.identity.domain.actors import Actor
from kernel.shared.domain.errors import DomainError


class GovernancePolicyViolationError(DomainError):
    """Raised when a claim violates governance policy."""


@dataclass(frozen=True, slots=True)
class CustodyDeclarationPolicy:
    """Policy that decides whether an actor may declare a custody claim."""

    policy_version: str = "governance/custody-declaration/v1"

    def authorize(self, actor: Actor | None, draft: CustodyAssertionDraft) -> None:
        """Validate that the draft provenance is allowed to enter Custody."""

        if actor is None:
            msg = f"unknown actor {draft.provenance.actor_id}"
            raise GovernancePolicyViolationError(msg)
        if not actor.can_declare_claims:
            msg = f"actor {actor.actor_id} cannot declare custody claims"
            raise GovernancePolicyViolationError(msg)

