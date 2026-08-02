from __future__ import annotations

from datetime import date
from uuid import uuid4

import pytest

from kernel.catalog.application.commands import RegisterCanonicalDevice
from kernel.catalog.application.services import DeviceCatalogService
from kernel.catalog.domain.device import (
    CatalogStatus,
    GmdnCode,
    IssuingAgency,
    ManufacturerIdentity,
    PackagingLevel,
    PackagingSpec,
    RegistrationStatus,
    RegulatoryRegistration,
    RiskClass,
    SterilizationCondition,
    StorageCondition,
    UdiDi,
)
from kernel.catalog.domain.errors import DeviceNotFoundError, DuplicateUdiDiError
from kernel.catalog.infrastructure.in_memory_device_repository import (
    InMemoryDeviceCatalogRepository,
)


def _command(udi_di_value: str = "UDI-DI:GTIN-001") -> RegisterCanonicalDevice:
    return RegisterCanonicalDevice(
        udi_di=UdiDi(value=udi_di_value, issuing_agency=IssuingAgency.GS1),
        generic_regulatory_name="External Fixation Screw",
        manufacturer=ManufacturerIdentity(legal_name="Acme Medical S.A.S."),
        manufacturer_model_reference="AFX-100",
        gmdn=GmdnCode(code="12345", term="Bone screw, non-bioabsorbable"),
        risk_class=RiskClass.CLASS_IIB,
        packaging=PackagingSpec(levels=(PackagingLevel(unit="each", quantity=1),)),
        unit_of_measure="unit",
        minimum_consumption_unit="unit",
        storage_conditions=StorageCondition(light_sensitive=False),
        sterilization=SterilizationCondition(is_sterile=True, method="ethylene_oxide"),
        commercial_presentation="Individually packaged, sterile",
    )


def test_register_assigns_device_id_and_defaults() -> None:
    service = DeviceCatalogService(InMemoryDeviceCatalogRepository())

    device = service.register(_command())

    assert device.device_id is not None
    assert device.lifecycle_status == CatalogStatus.DRAFT
    assert device.version == 1


def test_register_rejects_duplicate_udi_di() -> None:
    service = DeviceCatalogService(InMemoryDeviceCatalogRepository())
    service.register(_command("UDI-DI:GTIN-DUP"))

    with pytest.raises(DuplicateUdiDiError):
        service.register(_command("UDI-DI:GTIN-DUP"))


def test_get_returns_registered_device() -> None:
    service = DeviceCatalogService(InMemoryDeviceCatalogRepository())
    registered = service.register(_command())

    fetched = service.get(registered.device_id)

    assert fetched == registered


def test_get_raises_for_unknown_device() -> None:
    service = DeviceCatalogService(InMemoryDeviceCatalogRepository())

    with pytest.raises(DeviceNotFoundError):
        service.get(uuid4())


def test_find_by_udi_di_returns_none_when_unregistered() -> None:
    service = DeviceCatalogService(InMemoryDeviceCatalogRepository())

    assert service.find_by_udi_di("UDI-DI:UNKNOWN") is None


def test_with_status_increments_version_and_preserves_identity() -> None:
    device = DeviceCatalogService(InMemoryDeviceCatalogRepository()).register(_command())

    updated = device.with_status(CatalogStatus.ACTIVE)

    assert updated.device_id == device.device_id
    assert updated.lifecycle_status == CatalogStatus.ACTIVE
    assert updated.version == device.version + 1
    assert device.lifecycle_status == CatalogStatus.DRAFT  # original untouched (frozen)


def test_with_registration_added_appends_without_losing_existing() -> None:
    device = DeviceCatalogService(InMemoryDeviceCatalogRepository()).register(_command())
    registration = RegulatoryRegistration(
        registration_id=uuid4(),
        country="CO",
        authority="INVIMA",
        registration_number="INV-2026-001",
        valid_from=date(2026, 1, 1),
        valid_until=None,
        status=RegistrationStatus.ACTIVE,
    )

    updated = device.with_registration_added(registration)

    assert updated.regulatory_registrations == (registration,)
    assert device.regulatory_registrations == ()  # original untouched
