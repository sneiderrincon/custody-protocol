"""Actor registry port."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from kernel.identity.domain.actors import Actor


class ActorRegistry(Protocol):
    """Read port for actor identity and trust metadata."""

    def get(self, actor_id: UUID) -> Actor | None:
        """Return the actor for an identifier, if known."""

