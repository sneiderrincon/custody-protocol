"""SQLAlchemy implementation of the device catalog port."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from kernel.catalog.domain.device import (
    CanonicalDevice,
    GmdnCode,
    ManufacturerIdentity,
    PackagingSpec,
    RegulatoryRegistration,
    SterilizationCondition,
    StorageCondition,
    UdiDi,
)
from kernel.catalog.domain.errors import (
    ConcurrentCatalogUpdateError,
    DeviceNotFoundError,
    DuplicateUdiDiError,
)
from kernel.catalog.infrastructure.sqlalchemy_models import CanonicalDeviceRecord


class SqlAlchemyDeviceCatalogRepository:
    """PostgreSQL-backed device catalog repository.

    Like the custody SQLAlchemy adapters (see ADR 0006), this adapter is
    transaction-agnostic: it flushes so within-transaction reads see pending
    writes, but the caller (composition root) decides when to commit.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, device_id: UUID) -> CanonicalDevice | None:
        record = self._session.get(CanonicalDeviceRecord, str(device_id))
        return _record_to_device(record) if record is not None else None

    def find_by_udi_di(self, udi_di: str) -> CanonicalDevice | None:
        record = self._session.scalars(
            select(CanonicalDeviceRecord).where(CanonicalDeviceRecord.udi_di_value == udi_di)
        ).one_or_none()
        return _record_to_device(record) if record is not None else None

    def add(self, device: CanonicalDevice) -> CanonicalDevice:
        record = _device_to_record(device)
        self._session.add(record)
        try:
            self._session.flush()
        except IntegrityError as exc:
            self._session.rollback()
            msg = f"UDI-DI {device.udi_di.value} is already registered"
            raise DuplicateUdiDiError(msg) from exc
        return device

    def update(self, device: CanonicalDevice) -> CanonicalDevice:
        record = self._session.get(CanonicalDeviceRecord, str(device.device_id))
        if record is None:
            msg = f"no catalog entry for device_id {device.device_id}"
            raise DeviceNotFoundError(msg)
        if record.version >= device.version:
            msg = (
                f"device {device.device_id} version conflict: "
                f"stored version {record.version}, update targets {device.version}"
            )
            raise ConcurrentCatalogUpdateError(msg)
        _apply_device_to_record(device, record)
        self._session.flush()
        return device


def _device_to_record(device: CanonicalDevice) -> CanonicalDeviceRecord:
    return CanonicalDeviceRecord(
        device_id=str(device.device_id),
        udi_di_value=device.udi_di.value,
        udi_di_issuing_agency=device.udi_di.issuing_agency.value,
        generic_regulatory_name=device.generic_regulatory_name,
        manufacturer=device.manufacturer.model_dump(mode="json"),
        manufacturer_model_reference=device.manufacturer_model_reference,
        gmdn=device.gmdn.model_dump(mode="json"),
        risk_class=device.risk_class.value,
        regulatory_registrations=[
            registration.model_dump(mode="json") for registration in device.regulatory_registrations
        ],
        packaging=device.packaging.model_dump(mode="json"),
        unit_of_measure=device.unit_of_measure,
        minimum_consumption_unit=device.minimum_consumption_unit,
        storage_conditions=device.storage_conditions.model_dump(mode="json"),
        sterilization=device.sterilization.model_dump(mode="json"),
        commercial_presentation=device.commercial_presentation,
        lifecycle_status=device.lifecycle_status.value,
        version=device.version,
    )


def _apply_device_to_record(device: CanonicalDevice, record: CanonicalDeviceRecord) -> None:
    record.generic_regulatory_name = device.generic_regulatory_name
    record.manufacturer = device.manufacturer.model_dump(mode="json")
    record.manufacturer_model_reference = device.manufacturer_model_reference
    record.gmdn = device.gmdn.model_dump(mode="json")
    record.risk_class = device.risk_class.value
    record.regulatory_registrations = [
        registration.model_dump(mode="json") for registration in device.regulatory_registrations
    ]
    record.packaging = device.packaging.model_dump(mode="json")
    record.unit_of_measure = device.unit_of_measure
    record.minimum_consumption_unit = device.minimum_consumption_unit
    record.storage_conditions = device.storage_conditions.model_dump(mode="json")
    record.sterilization = device.sterilization.model_dump(mode="json")
    record.commercial_presentation = device.commercial_presentation
    record.lifecycle_status = device.lifecycle_status.value
    record.version = device.version


def _record_to_device(record: CanonicalDeviceRecord) -> CanonicalDevice:
    return CanonicalDevice(
        device_id=UUID(record.device_id),
        udi_di=UdiDi(value=record.udi_di_value, issuing_agency=record.udi_di_issuing_agency),
        generic_regulatory_name=record.generic_regulatory_name,
        manufacturer=ManufacturerIdentity.model_validate(record.manufacturer),
        manufacturer_model_reference=record.manufacturer_model_reference,
        gmdn=GmdnCode.model_validate(record.gmdn),
        risk_class=record.risk_class,
        regulatory_registrations=tuple(
            RegulatoryRegistration.model_validate(registration)
            for registration in record.regulatory_registrations
        ),
        packaging=PackagingSpec.model_validate(record.packaging),
        unit_of_measure=record.unit_of_measure,
        minimum_consumption_unit=record.minimum_consumption_unit,
        storage_conditions=StorageCondition.model_validate(record.storage_conditions),
        sterilization=SterilizationCondition.model_validate(record.sterilization),
        commercial_presentation=record.commercial_presentation,
        lifecycle_status=record.lifecycle_status,
        version=record.version,
    )
