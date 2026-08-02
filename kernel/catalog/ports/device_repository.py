"""Device Catalog repository port."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from kernel.catalog.domain.device import CanonicalDevice


class DeviceCatalogRepository(Protocol):
    """Read/write port for canonical device master data."""

    def get(self, device_id: UUID) -> CanonicalDevice | None:
        """Return the device for an identifier, if known."""

    def find_by_udi_di(self, udi_di: str) -> CanonicalDevice | None:
        """Return the device registered under a UDI-DI value, if any."""

    def add(self, device: CanonicalDevice) -> CanonicalDevice:
        """Persist a new device. Raises on a duplicate device_id or UDI-DI."""

    def update(self, device: CanonicalDevice) -> CanonicalDevice:
        """Persist an updated device using optimistic concurrency on `version`."""
