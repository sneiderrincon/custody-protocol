"""API dependency wiring."""

from __future__ import annotations

from functools import lru_cache

from kernel.custody.application.services import DeclareCustodyAssertionService
from kernel.custody.infrastructure.in_memory_event_store import InMemoryCustodyEventStore
from kernel.custody.infrastructure.in_memory_rejection_log import InMemoryRejectionLog


class KernelContainer:
    """Small composition root for local API execution."""

    def __init__(self) -> None:
        """Initialize local in-memory ports."""

        self.event_store = InMemoryCustodyEventStore()
        self.rejection_log = InMemoryRejectionLog()
        self.declare_service = DeclareCustodyAssertionService(
            self.event_store,
            rejection_log=self.rejection_log,
        )


@lru_cache
def get_container() -> KernelContainer:
    """Return the process-local kernel container."""

    return KernelContainer()

