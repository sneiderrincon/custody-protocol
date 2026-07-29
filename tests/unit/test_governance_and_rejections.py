from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from kernel.custody.application.commands import DeclareCustodyAssertion
from kernel.custody.application.services import DeclareCustodyAssertionService
from kernel.custody.domain.events import CustodyEventType, RejectionReason
from kernel.custody.domain.rules import RuleViolationError
from kernel.custody.domain.value_objects import Provenance
from kernel.custody.infrastructure.in_memory_event_store import InMemoryCustodyEventStore
from kernel.custody.infrastructure.in_memory_rejection_log import InMemoryRejectionLog
from kernel.governance.domain.policies import GovernancePolicyViolationError
from kernel.identity.domain.actors import Actor, ActorStatus, TrustLevel
from kernel.identity.infrastructure.in_memory_actor_registry import InMemoryActorRegistry


def test_governance_rejects_unknown_actor_and_records_rejection() -> None:
    registry = InMemoryActorRegistry()
    rejection_log = InMemoryRejectionLog()
    service = DeclareCustodyAssertionService(
        InMemoryCustodyEventStore(),
        actor_registry=registry,
        rejection_log=rejection_log,
    )

    with pytest.raises(GovernancePolicyViolationError):
        service.handle(_command(CustodyEventType.MANUFACTURED))

    rejection = rejection_log.all()[0]
    assert rejection.reason == RejectionReason.GOVERNANCE_VIOLATION


def test_precedence_rejection_does_not_append_custody_assertion() -> None:
    actor_id = uuid4()
    registry = InMemoryActorRegistry()
    registry.add(
        Actor(
            actor_id=actor_id,
            legal_name="Anchor Hospital",
            status=ActorStatus.ACTIVE,
            trust_level=TrustLevel.STANDARD,
        )
    )
    store = InMemoryCustodyEventStore()
    rejection_log = InMemoryRejectionLog()
    service = DeclareCustodyAssertionService(
        store,
        actor_registry=registry,
        rejection_log=rejection_log,
    )

    with pytest.raises(RuleViolationError):
        service.handle(_command(CustodyEventType.RECEIVED, actor_id=actor_id))

    assert store.all() == ()
    assert rejection_log.all()[0].reason == RejectionReason.PRECEDENCE_VIOLATION


def test_missing_actor_registry_fails_closed_and_records_rejection() -> None:
    rejection_log = InMemoryRejectionLog()
    service = DeclareCustodyAssertionService(
        InMemoryCustodyEventStore(),
        rejection_log=rejection_log,
    )

    with pytest.raises(GovernancePolicyViolationError):
        service.handle(_command(CustodyEventType.MANUFACTURED))

    rejection = rejection_log.all()[0]
    assert rejection.reason == RejectionReason.GOVERNANCE_VIOLATION


def test_active_actor_can_declare_custody_assertion() -> None:
    actor_id = uuid4()
    registry = InMemoryActorRegistry()
    registry.add(
        Actor(
            actor_id=actor_id,
            legal_name="Anchor Hospital",
            status=ActorStatus.ACTIVE,
            trust_level=TrustLevel.STANDARD,
        )
    )
    service = DeclareCustodyAssertionService(
        InMemoryCustodyEventStore(),
        actor_registry=registry,
    )

    assertion = service.handle(_command(CustodyEventType.MANUFACTURED, actor_id=actor_id))

    assert assertion.stream_version == 1


def _command(
    event_type: CustodyEventType,
    *,
    actor_id: object | None = None,
) -> DeclareCustodyAssertion:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    return DeclareCustodyAssertion(
        claim_id=uuid4(),
        unit_id="governance-unit",
        event_type=event_type,
        occurred_at=now,
        provenance=Provenance(
            actor_id=actor_id or uuid4(),
            adapter_id="governance-test-adapter",
            declared_at=now,
        ),
    )

