from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from kernel.custody.domain.assertions import CustodyAssertionDraft
from kernel.custody.domain.events import CustodyEventType
from kernel.custody.domain.value_objects import Provenance
from kernel.custody.infrastructure.in_memory_event_store import InMemoryCustodyEventStore
from kernel.shared.domain.errors import ConcurrencyConflictError, IdempotencyConflictError


def test_event_store_enforces_monotonic_global_positions() -> None:
    store = InMemoryCustodyEventStore()

    first = store.append(_draft(CustodyEventType.MANUFACTURED), expected_stream_version=0)
    second = store.append(
        _draft(CustodyEventType.MANUFACTURED, unit_id="unit-2"),
        expected_stream_version=0,
    )

    assert [event.global_position for event in store.all()] == [1, 2]
    assert first.stream_version == 1
    assert second.stream_version == 1


def test_event_store_rejects_wrong_expected_stream_version() -> None:
    store = InMemoryCustodyEventStore()

    with pytest.raises(ConcurrencyConflictError):
        store.append(_draft(CustodyEventType.MANUFACTURED), expected_stream_version=3)


def test_event_store_rejects_idempotency_key_reuse_with_different_content() -> None:
    store = InMemoryCustodyEventStore()
    claim_id = uuid4()
    first = _draft(CustodyEventType.MANUFACTURED, claim_id=claim_id)
    conflicting = _draft(CustodyEventType.SHIPPED, claim_id=claim_id)

    store.append(first, expected_stream_version=0)

    with pytest.raises(IdempotencyConflictError):
        store.append(conflicting, expected_stream_version=1)


def _draft(
    event_type: CustodyEventType,
    *,
    unit_id: str = "unit-1",
    claim_id: object | None = None,
) -> CustodyAssertionDraft:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    return CustodyAssertionDraft(
        claim_id=claim_id or uuid4(),
        unit_id=unit_id,
        event_type=event_type,
        occurred_at=now,
        provenance=Provenance(
            actor_id=uuid4(),
            adapter_id="event-store-contract",
            declared_at=now,
        ),
    )
