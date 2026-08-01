from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from kernel.custody.application.commands import DeclareCustodyAssertion
from kernel.custody.application.projections import CustodyProjectionEngine
from kernel.custody.application.services import DeclareCustodyAssertionService
from kernel.custody.domain.assertions import CommittedCustodyAssertion, CustodyAssertionDraft
from kernel.custody.domain.events import CustodyEventType
from kernel.custody.domain.rules import RuleViolationError
from kernel.custody.domain.value_objects import (
    AssertionPayload,
    EvidenceReference,
    PayloadAttribute,
    Provenance,
)
from kernel.custody.infrastructure.in_memory_event_store import InMemoryCustodyEventStore
from kernel.identity.domain.actors import Actor, ActorStatus, TrustLevel
from kernel.identity.infrastructure.in_memory_actor_registry import InMemoryActorRegistry

SHIPPED_STREAM_VERSION = 2
_ACTOR_ID = uuid4()


def _authorized_service(store: InMemoryCustodyEventStore) -> DeclareCustodyAssertionService:
    registry = InMemoryActorRegistry()
    registry.add(
        Actor(
            actor_id=_ACTOR_ID,
            legal_name="Conformance Test Actor",
            status=ActorStatus.ACTIVE,
            trust_level=TrustLevel.STANDARD,
        )
    )
    return DeclareCustodyAssertionService(store, actor_registry=registry)


def test_assertions_are_immutable_after_commit() -> None:
    store = InMemoryCustodyEventStore()
    service = _authorized_service(store)

    committed = service.handle(_command(CustodyEventType.MANUFACTURED))

    with pytest.raises(ValidationError):
        committed.event_type = CustodyEventType.SHIPPED  # type: ignore[misc]


def test_payload_is_deeply_immutable_enough_for_domain_use() -> None:
    payload = AssertionPayload(
        attributes=(PayloadAttribute(key="lot", value="LOT-001"),),
    )

    with pytest.raises(ValidationError):
        payload.attributes[0].value = "LOT-002"  # type: ignore[misc]

    with pytest.raises(TypeError):
        payload.attributes[0] = PayloadAttribute(key="lot", value="LOT-002")  # type: ignore[index]


def test_idempotent_command_returns_existing_committed_assertion() -> None:
    store = InMemoryCustodyEventStore()
    service = _authorized_service(store)
    command = _command(CustodyEventType.MANUFACTURED)

    first = service.handle(command)
    second = service.handle(command)

    assert first == second
    assert len(store.all()) == 1
    assert first.global_position == 1
    assert first.stream_version == 1


def test_invalid_precedence_is_rejected_before_append() -> None:
    store = InMemoryCustodyEventStore()
    service = _authorized_service(store)

    with pytest.raises(RuleViolationError, match="cannot start"):
        service.handle(_command(CustodyEventType.RECEIVED))

    assert store.all() == ()


def test_state_is_derived_by_replaying_history() -> None:
    store = InMemoryCustodyEventStore()
    service = _authorized_service(store)
    projection = CustodyProjectionEngine()
    manufactured = _command(CustodyEventType.MANUFACTURED)
    shipped = _command(
        CustodyEventType.SHIPPED,
        unit_id=manufactured.unit_id,
        occurred_at=datetime(2026, 1, 2, tzinfo=UTC),
    )

    service.handle(manufactured)
    service.handle(shipped)

    state = projection.state_at(
        manufactured.unit_id,
        datetime(2026, 1, 3, tzinfo=UTC),
        store.all(),
    )

    assert state.event_type == CustodyEventType.SHIPPED
    assert state.as_of_stream_version == SHIPPED_STREAM_VERSION


def test_committed_assertion_matches_draft_ignores_store_assigned_fields() -> None:
    command = _command(CustodyEventType.MANUFACTURED)
    draft = CustodyAssertionDraft(**command.model_dump())
    committed = CommittedCustodyAssertion(
        **draft.model_dump(), global_position=7, stream_version=3
    )

    assert committed.matches_draft(draft)

    different = _command(CustodyEventType.SHIPPED, unit_id=command.unit_id)
    assert not committed.matches_draft(CustodyAssertionDraft(**different.model_dump()))


def _command(
    event_type: CustodyEventType,
    *,
    unit_id: str = "UDI-DI:GTIN-001|SERIAL-001",
    occurred_at: datetime = datetime(2026, 1, 1, tzinfo=UTC),
) -> DeclareCustodyAssertion:
    return DeclareCustodyAssertion(
        claim_id=uuid4(),
        unit_id=unit_id,
        event_type=event_type,
        occurred_at=occurred_at,
        provenance=Provenance(
            actor_id=_ACTOR_ID,
            adapter_id="conformance-test-adapter",
            declared_at=occurred_at,
            evidence=(
                EvidenceReference(
                    uri="urn:evidence:test",
                    sha256="a" * 64,
                ),
            ),
        ),
    )
