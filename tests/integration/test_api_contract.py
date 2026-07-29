from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from api.dependencies import get_container
from api.main import create_app
from kernel.custody.domain.events import CustodyEventType

HTTP_OK = 200
HTTP_CREATED = 201
HTTP_UNPROCESSABLE_ENTITY = 422


def test_api_declares_and_reads_derived_state() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    now = datetime(2026, 1, 1, tzinfo=UTC)
    unit_id = "api-unit"

    response = client.post(
        "/v1/custody/assertions",
        json={
            "claim_id": str(uuid4()),
            "unit_id": unit_id,
            "event_type": CustodyEventType.MANUFACTURED.value,
            "occurred_at": now.isoformat(),
            "provenance": {
                "actor_id": str(uuid4()),
                "adapter_id": "api-test-adapter",
                "declared_at": now.isoformat(),
                "evidence": [],
            },
            "payload": {"attributes": []},
        },
    )

    assert response.status_code == HTTP_CREATED

    state_response = client.get(
        f"/v1/custody/units/{unit_id}/state",
        params={"at": now.isoformat()},
    )

    assert state_response.status_code == HTTP_OK
    assert state_response.json()["state"]["event_type"] == CustodyEventType.MANUFACTURED.value


def test_api_rejects_invalid_precedence_without_history() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    now = datetime(2026, 1, 1, tzinfo=UTC)

    response = client.post(
        "/v1/custody/assertions",
        json={
            "claim_id": str(uuid4()),
            "unit_id": "api-invalid-unit",
            "event_type": CustodyEventType.RECEIVED.value,
            "occurred_at": now.isoformat(),
            "provenance": {
                "actor_id": str(uuid4()),
                "adapter_id": "api-test-adapter",
                "declared_at": now.isoformat(),
            },
        },
    )

    assert response.status_code == HTTP_UNPROCESSABLE_ENTITY
