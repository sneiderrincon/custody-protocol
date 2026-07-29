"""Projection engine for derived custody reads."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from kernel.custody.domain.assertions import CommittedCustodyAssertion
from kernel.custody.domain.events import CustodyEventType


@dataclass(frozen=True, slots=True)
class CustodyStateProjection:
    """Derived state for a physical unit."""

    unit_id: str
    event_type: CustodyEventType | None
    as_of_stream_version: int


class CustodyProjectionEngine:
    """Pure projection engine that derives state by replaying the log."""

    def history(
        self,
        unit_id: str,
        log: tuple[CommittedCustodyAssertion, ...],
    ) -> tuple[CommittedCustodyAssertion, ...]:
        return tuple(event for event in log if event.unit_id == unit_id)

    def state_at(
        self,
        unit_id: str,
        at: datetime,
        log: tuple[CommittedCustodyAssertion, ...],
    ) -> CustodyStateProjection:
        events = tuple(
            event
            for event in self.history(unit_id, log)
            if event.occurred_at <= at
        )
        if not events:
            return CustodyStateProjection(unit_id, None, 0)
        latest = events[-1]
        return CustodyStateProjection(unit_id, latest.event_type, latest.stream_version)

