"""Device Catalog write commands."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from kernel.catalog.domain.device import (
    GmdnCode,
    ManufacturerIdentity,
    PackagingSpec,
    RiskClass,
    SterilizationCondition,
    StorageCondition,
    UdiDi,
)


class RegisterCanonicalDevice(BaseModel):
    """Command to register a new device in the canonical catalog.

    device_id, lifecycle_status, and version are server-assigned -- a caller
    never dictates the internal identity or starting lifecycle of a catalog
    entry, mirroring how DeclareCustodyAssertion never lets a caller assign
    global_position/stream_version.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    udi_di: UdiDi
    generic_regulatory_name: str
    manufacturer: ManufacturerIdentity
    manufacturer_model_reference: str
    gmdn: GmdnCode
    risk_class: RiskClass
    packaging: PackagingSpec
    unit_of_measure: str
    minimum_consumption_unit: str
    storage_conditions: StorageCondition
    sterilization: SterilizationCondition
    commercial_presentation: str
