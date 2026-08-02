"""Device Catalog application service."""

from __future__ import annotations

from uuid import UUID, uuid4

from kernel.catalog.application.commands import RegisterCanonicalDevice
from kernel.catalog.domain.device import CanonicalDevice
from kernel.catalog.domain.errors import DeviceNotFoundError, DuplicateUdiDiError
from kernel.catalog.ports.device_repository import DeviceCatalogRepository


class DeviceCatalogService:
    """Use cases for registering and reading canonical device master data."""

    def __init__(self, repository: DeviceCatalogRepository) -> None:
        self._repository = repository

    def register(self, command: RegisterCanonicalDevice) -> CanonicalDevice:
        """Register a new canonical device. Rejects a duplicate UDI-DI."""

        existing = self._repository.find_by_udi_di(command.udi_di.value)
        if existing is not None:
            msg = f"UDI-DI {command.udi_di.value} is already registered as {existing.device_id}"
            raise DuplicateUdiDiError(msg)

        device = CanonicalDevice(device_id=uuid4(), **command.model_dump())
        return self._repository.add(device)

    def get(self, device_id: UUID) -> CanonicalDevice:
        """Return a device by its internal identifier. Raises if unknown."""

        device = self._repository.get(device_id)
        if device is None:
            msg = f"no catalog entry for device_id {device_id}"
            raise DeviceNotFoundError(msg)
        return device

    def find_by_udi_di(self, udi_di: str) -> CanonicalDevice | None:
        """Return a device by its UDI-DI, or None if not registered."""

        return self._repository.find_by_udi_di(udi_di)
