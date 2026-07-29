"""Example: declare a custody assertion through the application service."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from kernel.custody.application.commands import DeclareCustodyAssertion
from kernel.custody.application.services import DeclareCustodyAssertionService
from kernel.custody.domain.events import CustodyEventType
from kernel.custody.domain.value_objects import EvidenceReference, Provenance
from kernel.custody.infrastructure.in_memory_event_store import InMemoryCustodyEventStore


def main() -> None:
    """Run the example and print the committed assertion."""

    now = datetime.now(UTC)
    service = DeclareCustodyAssertionService(InMemoryCustodyEventStore())
    assertion = service.handle(
        DeclareCustodyAssertion(
            claim_id=uuid4(),
            unit_id="UDI-DI:GTIN-09506000134352|SERIAL-0001",
            event_type=CustodyEventType.MANUFACTURED,
            occurred_at=now,
            provenance=Provenance(
                actor_id=uuid4(),
                adapter_id="example-adapter",
                declared_at=now,
                evidence=(
                    EvidenceReference(
                        uri="urn:example:evidence:manufacturing-order",
                        sha256="b" * 64,
                    ),
                ),
            ),
        )
    )
    print(assertion.model_dump_json(indent=2))


if __name__ == "__main__":
    main()

