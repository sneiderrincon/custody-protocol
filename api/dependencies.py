"""API dependency wiring."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from kernel.catalog.application.services import DeviceCatalogService
from kernel.catalog.domain.device import CanonicalDevice
from kernel.catalog.infrastructure.in_memory_device_repository import (
    InMemoryDeviceCatalogRepository,
)
from kernel.catalog.infrastructure.sqlalchemy_repository import SqlAlchemyDeviceCatalogRepository
from kernel.catalog.ports.device_repository import DeviceCatalogRepository
from kernel.custody.application.services import DeclareCustodyAssertionService
from kernel.custody.domain.assertions import CommittedCustodyAssertion, CustodyAssertionDraft
from kernel.custody.domain.rejections import RejectedInconsistency
from kernel.custody.infrastructure.in_memory_event_store import InMemoryCustodyEventStore
from kernel.custody.infrastructure.in_memory_rejection_log import InMemoryRejectionLog
from kernel.custody.infrastructure.sqlalchemy_event_store import (
    SqlAlchemyCustodyEventStore,
    SqlAlchemyRejectionLog,
)
from kernel.custody.ports.event_store import CustodyEventStore
from kernel.custody.ports.rejection_log import RejectionLog
from kernel.identity.domain.actors import Actor, ActorStatus, TrustLevel
from kernel.identity.infrastructure.in_memory_actor_registry import InMemoryActorRegistry
from kernel.identity.ports.actor_registry import ActorRegistry
from kernel.shared.infrastructure.database import build_session_factory



@dataclass
class _CommittingCustodyEventStore:
    """Commits the bound session after each successful append.

    ``KernelContainer`` holds one long-lived session for the process, so each
    mutating call must be committed individually for custody assertions to be
    durable across requests and process restarts. The wrapped
    ``SqlAlchemyCustodyEventStore`` deliberately leaves transaction boundaries
    to its caller (see tests/integration/test_sqlalchemy_event_store.py), so
    the composition root owns that decision here.
    """

    _inner: SqlAlchemyCustodyEventStore
    _session: Session

    def stream(self, unit_id: str) -> tuple[CommittedCustodyAssertion, ...]:
        return self._inner.stream(unit_id)

    def append(
        self,
        draft: CustodyAssertionDraft,
        *,
        expected_stream_version: int,
    ) -> CommittedCustodyAssertion:
        committed = self._inner.append(draft, expected_stream_version=expected_stream_version)
        self._session.commit()
        return committed

    def by_claim_id(self, claim_id: UUID) -> CommittedCustodyAssertion | None:
        return self._inner.by_claim_id(claim_id)

    def all(self) -> tuple[CommittedCustodyAssertion, ...]:
        return self._inner.all()


@dataclass
class _CommittingRejectionLog:
    """Commits the bound session after each successful rejection append."""

    _inner: SqlAlchemyRejectionLog
    _session: Session

    def append(self, rejection: RejectedInconsistency) -> RejectedInconsistency:
        result = self._inner.append(rejection)
        self._session.commit()
        return result

    def all(self) -> tuple[RejectedInconsistency, ...]:
        return self._inner.all()


@dataclass
class _CommittingDeviceCatalogRepository:
    """Commits the bound session after each successful write.

    Same reasoning as ``_CommittingCustodyEventStore``: the SQLAlchemy
    repository leaves transaction boundaries to its caller, and
    ``KernelContainer`` is the long-lived composition root that owns them.
    """

    _inner: SqlAlchemyDeviceCatalogRepository
    _session: Session

    def get(self, device_id: UUID) -> CanonicalDevice | None:
        return self._inner.get(device_id)

    def find_by_udi_di(self, udi_di: str) -> CanonicalDevice | None:
        return self._inner.find_by_udi_di(udi_di)

    def add(self, device: CanonicalDevice) -> CanonicalDevice:
        result = self._inner.add(device)
        self._session.commit()
        return result

    def update(self, device: CanonicalDevice) -> CanonicalDevice:
        result = self._inner.update(device)
        self._session.commit()
        return result


class KernelContainer:
    """Small composition root for local API execution."""

    def __init__(self) -> None:
        """Wire ports from ``DATABASE_URL`` when configured, else in-memory."""

        database_url = os.getenv("DATABASE_URL")
        self.event_store: CustodyEventStore
        self.rejection_log: RejectionLog
        self.device_catalog: DeviceCatalogRepository
        
        self._session: Session | None = None
        self.actor_registry: ActorRegistry = InMemoryActorRegistry()
        self.actor_registry.add(
            Actor(
            actor_id=UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6"),
            legal_name="Development Actor",
            status=ActorStatus.ACTIVE,
            trust_level=TrustLevel.HIGH,
        )
)

        if database_url:
            session = build_session_factory(database_url)()
            self._session = session
            self.event_store = _CommittingCustodyEventStore(
                SqlAlchemyCustodyEventStore(session), session
            )
            self.rejection_log = _CommittingRejectionLog(
                SqlAlchemyRejectionLog(session), session
            )
            self.device_catalog = _CommittingDeviceCatalogRepository(
                SqlAlchemyDeviceCatalogRepository(session), session
            )
        else:
            self.event_store = InMemoryCustodyEventStore()
            self.rejection_log = InMemoryRejectionLog()
            self.device_catalog = InMemoryDeviceCatalogRepository()

        self.declare_service = DeclareCustodyAssertionService(
            self.event_store,
            actor_registry=self.actor_registry,
            rejection_log=self.rejection_log,
        )
        self.catalog_service = DeviceCatalogService(self.device_catalog)

    def ping(self) -> None:
        """Verify the backing store is reachable; raises if not.

        Used by the health endpoint (api/routes/health.py) and by startup
        validation (api/main.py) for readiness checks. In-memory mode has no
        external dependency to verify, so this is a no-op in that case.
        """

        if self._session is not None:
            self._session.execute(text("SELECT 1"))


@lru_cache
def get_container() -> KernelContainer:
    """Return the process-local kernel container."""

    return KernelContainer()

