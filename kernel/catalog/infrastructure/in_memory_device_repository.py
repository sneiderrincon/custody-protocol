"""In-memory device catalog repository for tests and local execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from kernel.catalog.domain.device import CanonicalDevice
from kernel.catalog.domain.errors import (
    ConcurrentCatalogUpdateError,
    DeviceNotFoundError,
    DuplicateUdiDiError,
)


@dataclass
class InMemoryDeviceCatalogRepository:
    """Mutable in-memory catalog used outside the domain layer."""

    _by_id: dict[UUID, CanonicalDevice] = field(default_factory=dict)
    _by_udi_di: dict[str, UUID] = field(default_factory=dict)

    def get(self, device_id: UUID) -> CanonicalDevice | None:
        return self._by_id.get(device_id)

    def find_by_udi_di(self, udi_di: str) -> CanonicalDevice | None:
        device_id = self._by_udi_di.get(udi_di)
        return self._by_id.get(device_id) if device_id is not None else None

    def add(self, device: CanonicalDevice) -> CanonicalDevice:
        if device.udi_di.value in self._by_udi_di:
            msg = f"UDI-DI {device.udi_di.value} is already registered"
            raise DuplicateUdiDiError(msg)
        self._by_id[device.device_id] = device
        self._by_udi_di[device.udi_di.value] = device.device_id
        return device

    def update(self, device: CanonicalDevice) -> CanonicalDevice:
        current = self._by_id.get(device.device_id)
        if current is None:
            msg = f"no catalog entry for device_id {device.device_id}"
            raise DeviceNotFoundError(msg)
        if current.version >= device.version:
            msg = (
                f"device {device.device_id} version conflict: "
                f"stored version {current.version}, update targets {device.version}"
            )
            raise ConcurrentCatalogUpdateError(msg)
        self._by_id[device.device_id] = device
        return device
