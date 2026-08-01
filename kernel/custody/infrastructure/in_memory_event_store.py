"""In-memory append-only event store for tests and local conformance."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from kernel.custody.domain.assertions import CommittedCustodyAssertion, CustodyAssertionDraft
from kernel.shared.domain.errors import ConcurrencyConflictError, IdempotencyConflictError


@dataclass
class InMemoryCustodyEventStore:
    """Append-only store with idempotency and optimistic stream checks."""

    _log: list[CommittedCustodyAssertion] = field(default_factory=list)
    _by_claim_id: dict[UUID, CommittedCustodyAssertion] = field(default_factory=dict)

    def stream(self, unit_id: str) -> tuple[CommittedCustodyAssertion, ...]:
        return tuple(event for event in self._log if event.unit_id == unit_id)

    def append(
        self,
        draft: CustodyAssertionDraft,
        *,
        expected_stream_version: int,
    ) -> CommittedCustodyAssertion:
        existing = self._by_claim_id.get(draft.claim_id)
        if existing is not None:
            if existing.matches_draft(draft):
                return existing
            msg = f"claim_id {draft.claim_id} was reused for different assertion content"
            raise IdempotencyConflictError(msg)

        current_stream = self.stream(draft.unit_id)
        if len(current_stream) != expected_stream_version:
            msg = (
                f"expected stream version {expected_stream_version}, "
                f"found {len(current_stream)} for unit {draft.unit_id}"
            )
            raise ConcurrencyConflictError(msg)

        committed = CommittedCustodyAssertion(
            **draft.model_dump(),
            global_position=len(self._log) + 1,
            stream_version=len(current_stream) + 1,
        )
        self._log.append(committed)
        self._by_claim_id[committed.claim_id] = committed
        return committed

    def by_claim_id(self, claim_id: UUID) -> CommittedCustodyAssertion | None:
        return self._by_claim_id.get(claim_id)

    def all(self) -> tuple[CommittedCustodyAssertion, ...]:
        return tuple(self._log)

