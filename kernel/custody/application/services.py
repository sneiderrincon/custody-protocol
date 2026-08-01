"""Custody application services."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from kernel.custody.application.commands import DeclareCustodyAssertion
from kernel.custody.domain.aggregate import DeviceCustodyAggregate
from kernel.custody.domain.assertions import CommittedCustodyAssertion, CustodyAssertionDraft
from kernel.custody.domain.events import RejectionReason
from kernel.custody.domain.rejections import RejectedInconsistency
from kernel.custody.domain.rules import (
    PrecedenceViolationError,
    RuleViolationError,
    TemporalViolationError,
    VersionedCustodyRuleEngine,
)
from kernel.custody.ports.event_store import CustodyEventStore
from kernel.custody.ports.rejection_log import RejectionLog
from kernel.governance.domain.policies import (
    CustodyDeclarationPolicy,
    GovernancePolicyViolationError,
)
from kernel.identity.ports.actor_registry import ActorRegistry
from kernel.shared.domain.errors import ConcurrencyConflictError, IdempotencyConflictError


class DeclareCustodyAssertionService:
    """Use case for declaring a custody assertion.

    The service orchestrates ports and domain services. It does not derive state or persist
    projections. Rejected attempts are written to the rejection log when one is configured.
    """

    def __init__(
        self,
        event_store: CustodyEventStore,
        rule_engine: VersionedCustodyRuleEngine | None = None,
        actor_registry: ActorRegistry | None = None,
        declaration_policy: CustodyDeclarationPolicy | None = None,
        rejection_log: RejectionLog | None = None,
    ) -> None:
        self._event_store = event_store
        self._rule_engine = rule_engine or VersionedCustodyRuleEngine()
        self._actor_registry = actor_registry
        self._declaration_policy = declaration_policy or CustodyDeclarationPolicy()
        self._rejection_log = rejection_log

    def handle(self, command: DeclareCustodyAssertion) -> CommittedCustodyAssertion:
        """Validate and append a custody assertion."""

        draft = CustodyAssertionDraft(**command.model_dump())

        try:
            self._authorize(draft)
            existing = self._event_store.by_claim_id(draft.claim_id)
            if existing is not None:
                return self._event_store.append(
                    draft,
                    expected_stream_version=existing.stream_version - 1,
                )

            history = self._event_store.stream(draft.unit_id)
            aggregate = DeviceCustodyAggregate.rehydrate(draft.unit_id, history)
            self._rule_engine.validate(draft, aggregate.history)
            return self._event_store.append(draft, expected_stream_version=aggregate.version)
        except GovernancePolicyViolationError as exc:
            self._record_rejection(draft, RejectionReason.GOVERNANCE_VIOLATION, exc)
            raise
        except RuleViolationError as exc:
            reason = _rule_rejection_reason(exc)
            self._record_rejection(draft, reason, exc)
            raise
        except IdempotencyConflictError as exc:
            self._record_rejection(draft, RejectionReason.IDEMPOTENCY_CONFLICT, exc)
            raise
        except ConcurrencyConflictError as exc:
            self._record_rejection(draft, RejectionReason.CONCURRENCY_CONFLICT, exc)
            raise

    def _authorize(self, draft: CustodyAssertionDraft) -> None:
        if self._actor_registry is None:
            msg = "no actor registry configured; custody declarations cannot be authorized"
            raise GovernancePolicyViolationError(msg)
        actor = self._actor_registry.get(draft.provenance.actor_id)
        self._declaration_policy.authorize(actor, draft)

    def _record_rejection(
        self,
        draft: CustodyAssertionDraft,
        reason: RejectionReason,
        error: Exception,
    ) -> None:
        if self._rejection_log is None:
            return
        self._rejection_log.append(
            RejectedInconsistency(
                rejection_id=uuid4(),
                attempted_claim_id=draft.claim_id,
                unit_id=draft.unit_id,
                event_type=draft.event_type,
                reason=reason,
                detail=str(error),
                rejected_at=datetime.now(UTC),
                provenance=draft.provenance,
            )
        )


def _rule_rejection_reason(error: RuleViolationError) -> RejectionReason:
    if isinstance(error, TemporalViolationError):
        return RejectionReason.TEMPORAL_VIOLATION
    if isinstance(error, PrecedenceViolationError):
        return RejectionReason.PRECEDENCE_VIOLATION
    msg = f"unclassified rule violation: {error}"
    raise NotImplementedError(msg)
