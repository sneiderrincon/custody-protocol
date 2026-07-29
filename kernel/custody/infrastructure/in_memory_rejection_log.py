"""In-memory append-only rejection log."""

from __future__ import annotations

from dataclasses import dataclass, field

from kernel.custody.domain.rejections import RejectedInconsistency


@dataclass
class InMemoryRejectionLog:
    """Append-only rejection log for tests and local execution."""

    _events: list[RejectedInconsistency] = field(default_factory=list)

    def append(self, rejection: RejectedInconsistency) -> RejectedInconsistency:
        """Append a rejection event."""

        self._events.append(rejection)
        return rejection

    def all(self) -> tuple[RejectedInconsistency, ...]:
        """Return all rejection events in append order."""

        return tuple(self._events)

