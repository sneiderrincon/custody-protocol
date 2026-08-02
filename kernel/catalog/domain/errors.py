"""Device Catalog domain errors."""

from __future__ import annotations

from kernel.shared.domain.errors import DomainError


class DuplicateUdiDiError(DomainError):
    """Raised when registering a UDI-DI that already exists in the catalog."""


class DeviceNotFoundError(DomainError):
    """Raised when a referenced device_id has no catalog entry."""


class ConcurrentCatalogUpdateError(DomainError):
    """Raised when an update targets a stale catalog entry version."""
