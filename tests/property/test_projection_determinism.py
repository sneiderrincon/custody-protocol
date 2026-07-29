from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from hypothesis import given
from hypothesis import strategies as st

from kernel.custody.application.commands import DeclareCustodyAssertion
from kernel.custody.application.projections import CustodyProjectionEngine
from kernel.custody.application.services import DeclareCustodyAssertionService
from kernel.custody.domain.events import CustodyEventType
from kernel.custody.domain.value_objects import Provenance
from kernel.custody.infrastructure.in_memory_event_store import InMemoryCustodyEventStore
from kernel.identity.domain.actors import Actor, ActorStatus, TrustLevel
from kernel.identity.infrastructure.in_memory_actor_registry import InMemoryActorRegistry


@given(st.integers(min_value=1, max_value=5))
def test_projection_is_deterministic_for_same_log(length: int) -> None:
    store = InMemoryCustodyEventStore()
    actor_id = uuid4()
    registry = InMemoryActorRegistry()
    registry.add(
        Actor(
            actor_id=actor_id,
            legal_name="Property Test Actor",
            status=ActorStatus.ACTIVE,
            trust_level=TrustLevel.STANDARD,
        )
    )
    service = DeclareCustodyAssertionService(store, actor_registry=registry)
    projection = CustodyProjectionEngine()
    unit_id = "property-unit"
    start = datetime(2026, 1, 1, tzinfo=UTC)

    for index, event_type in enumerate(_valid_prefix(length), start=0):
        service.handle(
            DeclareCustodyAssertion(
                claim_id=uuid4(),
                unit_id=unit_id,
                event_type=event_type,
                occurred_at=start + timedelta(days=index),
                provenance=Provenance(
                    actor_id=actor_id,
                    adapter_id="property-test-adapter",
                    declared_at=start + timedelta(days=index),
                ),
            )
        )

    log = store.all()
    first = projection.state_at(unit_id, start + timedelta(days=99), log)
    second = projection.state_at(unit_id, start + timedelta(days=99), tuple(log))

    assert first == second


def _valid_prefix(length: int) -> tuple[CustodyEventType, ...]:
    path = (
        CustodyEventType.MANUFACTURED,
        CustodyEventType.SHIPPED,
        CustodyEventType.RECEIVED,
        CustodyEventType.DISPATCHED,
        CustodyEventType.USED_IMPLANTED,
    )
    return path[:length]

