"""In-memory actor registry for tests and local execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from kernel.identity.domain.actors import Actor


@dataclass
class InMemoryActorRegistry:
    """Mutable in-memory registry used outside the domain layer."""

    _actors: dict[UUID, Actor] = field(default_factory=dict)

    def add(self, actor: Actor) -> None:
        """Register or replace an actor in local memory."""

        self._actors[actor.actor_id] = actor

    def get(self, actor_id: UUID) -> Actor | None:
        """Return the actor for an identifier, if known."""

        return self._actors.get(actor_id)

