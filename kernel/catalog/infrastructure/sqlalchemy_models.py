"""SQLAlchemy mapping for device catalog persistence."""

from __future__ import annotations

from sqlalchemy import JSON, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from kernel.shared.infrastructure.database import Base


class CanonicalDeviceRecord(Base):
    """ORM row for a canonical device catalog entry.

    Nested value objects (udi_di, manufacturer, gmdn, packaging,
    storage_conditions, sterilization, regulatory_registrations) are stored as
    JSON columns rather than normalized child tables. This is a deliberate V1
    trade-off: nothing in this increment queries by, say, "devices with an
    expiring registration" -- when that need is real, normalizing
    regulatory_registrations into its own table is a contained migration, not
    a rewrite (see docs/decisions/0015-device-catalog.md).
    """

    __tablename__ = "catalog_devices"
    __table_args__ = (UniqueConstraint("udi_di_value", name="uq_catalog_devices_udi_di"),)

    device_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    udi_di_value: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    udi_di_issuing_agency: Mapped[str] = mapped_column(String(16), nullable=False)
    generic_regulatory_name: Mapped[str] = mapped_column(String(512), nullable=False)
    manufacturer: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    manufacturer_model_reference: Mapped[str] = mapped_column(String(255), nullable=False)
    gmdn: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    risk_class: Mapped[str] = mapped_column(String(8), nullable=False)
    regulatory_registrations: Mapped[list[object]] = mapped_column(JSON, nullable=False)
    packaging: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(String(64), nullable=False)
    minimum_consumption_unit: Mapped[str] = mapped_column(String(64), nullable=False)
    storage_conditions: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    sterilization: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    commercial_presentation: Mapped[str] = mapped_column(String(512), nullable=False)
    lifecycle_status: Mapped[str] = mapped_column(String(16), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
