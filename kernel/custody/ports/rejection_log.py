"""Rejection log port."""

from __future__ import annotations

from typing import Protocol

from kernel.custody.domain.rejections import RejectedInconsistency


class RejectionLog(Protocol):
    """Append-only persistence port for rejected inconsistency events."""

    def append(self, rejection: RejectedInconsistency) -> RejectedInconsistency:
        """Append a rejection event."""

    def all(self) -> tuple[RejectedInconsistency, ...]:
        """Return all rejection events in append order."""

