"""Custody aggregate."""

from __future__ import annotations

from dataclasses import dataclass

from kernel.custody.domain.assertions import CommittedCustodyAssertion


@dataclass(frozen=True, slots=True)
class DeviceCustodyAggregate:
    """A physical unit represented by its complete custody event stream."""

    unit_id: str
    history: tuple[CommittedCustodyAssertion, ...]

    @property
    def version(self) -> int:
        return len(self.history)

    @classmethod
    def rehydrate(
        cls,
        unit_id: str,
        history: tuple[CommittedCustodyAssertion, ...],
    ) -> DeviceCustodyAggregate:
        return cls(unit_id=unit_id, history=history)
