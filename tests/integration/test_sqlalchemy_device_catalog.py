from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from kernel.catalog.application.commands import RegisterCanonicalDevice
from kernel.catalog.application.services import DeviceCatalogService
from kernel.catalog.domain.device import (
    GmdnCode,
    IssuingAgency,
    ManufacturerIdentity,
    PackagingLevel,
    PackagingSpec,
    RiskClass,
    SterilizationCondition,
    StorageCondition,
    UdiDi,
)
from kernel.catalog.domain.errors import (
    ConcurrentCatalogUpdateError,
    DeviceNotFoundError,
    DuplicateUdiDiError,
)
from kernel.catalog.infrastructure.sqlalchemy_repository import SqlAlchemyDeviceCatalogRepository
from kernel.shared.infrastructure.database import Base


def _command(udi_di_value: str) -> RegisterCanonicalDevice:
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


def test_sqlalchemy_repository_round_trips_a_device() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        repository = SqlAlchemyDeviceCatalogRepository(session)
        service = DeviceCatalogService(repository)
        registered = service.register(_command("UDI-DI:GTIN-SQL-001"))
        session.commit()

        fetched_by_id = repository.get(registered.device_id)
        fetched_by_udi_di = repository.find_by_udi_di("UDI-DI:GTIN-SQL-001")

    assert fetched_by_id == registered
    assert fetched_by_udi_di == registered
    assert fetched_by_id.regulatory_registrations == ()


def test_sqlalchemy_repository_rejects_duplicate_udi_di() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        repository = SqlAlchemyDeviceCatalogRepository(session)
        service = DeviceCatalogService(repository)
        service.register(_command("UDI-DI:GTIN-DUP-SQL"))
        session.commit()

        with pytest.raises(DuplicateUdiDiError):
            service.register(_command("UDI-DI:GTIN-DUP-SQL"))


def test_sqlalchemy_repository_update_enforces_optimistic_concurrency() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        repository = SqlAlchemyDeviceCatalogRepository(session)
        service = DeviceCatalogService(repository)
        device = service.register(_command("UDI-DI:GTIN-CONCURRENCY"))
        session.commit()

        updated = repository.update(device.with_status(device.lifecycle_status))
        session.commit()
        assert updated.version == device.version + 1

        with pytest.raises(ConcurrentCatalogUpdateError):
            # Reusing the stale `device` (version 1) after the store has moved to version 2.
            repository.update(device.with_status(device.lifecycle_status))


def test_sqlalchemy_repository_update_raises_for_unknown_device() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        repository = SqlAlchemyDeviceCatalogRepository(session)
        never_registered = DeviceCatalogService(repository).register(
            _command("UDI-DI:GTIN-GHOST")
        )
        session.rollback()  # undo the registration -- the row never actually persists

        with pytest.raises(DeviceNotFoundError):
            repository.update(never_registered.with_status(never_registered.lifecycle_status))
