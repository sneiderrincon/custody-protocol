"""Event store port for custody assertions."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from kernel.custody.domain.assertions import CommittedCustodyAssertion, CustodyAssertionDraft


class CustodyEventStore(Protocol):
    """Append-only persistence port for custody claims."""

    def stream(self, unit_id: str) -> tuple[CommittedCustodyAssertion, ...]:
        """Return the immutable stream for a physical unit."""

    def append(
        self,
        draft: CustodyAssertionDraft,
        *,
        expected_stream_version: int,
    ) -> CommittedCustodyAssertion:
        """Append a new assertion exactly once."""

    def by_claim_id(self, claim_id: UUID) -> CommittedCustodyAssertion | None:
        """Return an assertion by idempotency key."""

    def all(self) -> tuple[CommittedCustodyAssertion, ...]:
        """Return the global append-only log in position order."""

