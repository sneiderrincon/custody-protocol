"""Device Catalog domain model.

The canonical, regulatory-truth identity of a medical device model. This is
master data, not a custody fact: it answers "what is this device, officially"
(UDI-DI, GMDN, manufacturer, risk class, registrations), never "who currently
holds a physical unit of it" -- that remains the Custody Kernel's job,
untouched, referenced only by device_id (see docs/decisions/0015-device-catalog.md).
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IssuingAgency(StrEnum):
    """UDI issuing agency accredited to assign a UDI-DI."""

    GS1 = "GS1"
    HIBCC = "HIBCC"
    ICCBBA = "ICCBBA"


class RiskClass(StrEnum):
    """Medical device risk classification."""

    CLASS_I = "I"
    CLASS_IIA = "IIa"
    CLASS_IIB = "IIb"
    CLASS_III = "III"


class CatalogStatus(StrEnum):
    """Lifecycle status of a catalog entry (distinct from any single unit's custody state)."""

    DRAFT = "draft"
    ACTIVE = "active"
    DISCONTINUED = "discontinued"
    RECALLED = "recalled"


class RegistrationStatus(StrEnum):
    """Lifecycle status of a single regulatory registration."""

    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


class UdiDi(BaseModel):
    """Unique Device Identifier - Device Identifier, as assigned by an issuing agency."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    value: str = Field(min_length=1)
    issuing_agency: IssuingAgency


class ManufacturerIdentity(BaseModel):
    """Legal manufacturer identity, distinct from any distributor/reseller name."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    legal_name: str = Field(min_length=1)
    invima_manufacturer_id: str | None = None


class GmdnCode(BaseModel):
    """Global Medical Device Nomenclature classification."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    code: str = Field(min_length=1)
    term: str = Field(min_length=1)


class PackagingLevel(BaseModel):
    """A single level of a device's packaging hierarchy (e.g. each, box, case)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    unit: str = Field(min_length=1)
    quantity: int = Field(ge=1)


class PackagingSpec(BaseModel):
    """Full packaging hierarchy for a device."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    levels: tuple[PackagingLevel, ...] = Field(min_length=1)


class StorageCondition(BaseModel):
    """Required storage conditions for the device."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    temperature_min_celsius: float | None = None
    temperature_max_celsius: float | None = None
    humidity_max_percent: float | None = None
    light_sensitive: bool = False


class SterilizationCondition(BaseModel):
    """Sterilization state and method, when applicable."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    is_sterile: bool
    method: str | None = None


class RegulatoryRegistration(BaseModel):
    """A single country/authority regulatory registration for a device (e.g. INVIMA)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    registration_id: UUID
    country: str = Field(min_length=2, max_length=2)
    authority: str = Field(min_length=1)
    registration_number: str = Field(min_length=1)
    valid_from: date
    valid_until: date | None = None
    status: RegistrationStatus


class CanonicalDevice(BaseModel):
    """Aggregate root: the single regulatory identity of a physical medical device model.

    Immutable value semantics (frozen); mutation methods return a new instance
    with `version` incremented, mirroring optimistic-concurrency conventions
    already used elsewhere in this kernel (CommittedCustodyAssertion.stream_version).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    device_id: UUID
    udi_di: UdiDi
    generic_regulatory_name: str = Field(min_length=1)
    manufacturer: ManufacturerIdentity
    manufacturer_model_reference: str = Field(min_length=1)
    gmdn: GmdnCode
    risk_class: RiskClass
    regulatory_registrations: tuple[RegulatoryRegistration, ...] = ()
    packaging: PackagingSpec
    unit_of_measure: str = Field(min_length=1)
    minimum_consumption_unit: str = Field(min_length=1)
    storage_conditions: StorageCondition
    sterilization: SterilizationCondition
    commercial_presentation: str = Field(min_length=1)
    lifecycle_status: CatalogStatus = CatalogStatus.DRAFT
    version: int = Field(ge=1, default=1)

    def with_registration_added(self, registration: RegulatoryRegistration) -> CanonicalDevice:
        """Return a new CanonicalDevice with an additional regulatory registration."""

        return self.model_copy(
            update={
                "regulatory_registrations": (*self.regulatory_registrations, registration),
                "version": self.version + 1,
            }
        )

    def with_status(self, status: CatalogStatus) -> CanonicalDevice:
        """Return a new CanonicalDevice with an updated lifecycle status."""

        return self.model_copy(update={"lifecycle_status": status, "version": self.version + 1})
