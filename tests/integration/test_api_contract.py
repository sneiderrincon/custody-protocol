from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

import jwt
from fastapi.testclient import TestClient

from api.dependencies import get_container
from api.main import create_app
from api.rate_limit import get_write_rate_limiter
from api.security import ALGORITHM
from kernel.custody.domain.events import CustodyEventType
from kernel.identity.domain.actors import Actor, ActorStatus, TrustLevel

HTTP_OK = 200
HTTP_CREATED = 201
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_UNPROCESSABLE_ENTITY = 422
HTTP_TOO_MANY_REQUESTS = 429

JWT_TEST_SECRET = "test-secret-do-not-use-in-production"  # noqa: S105


def _register_active_actor(actor_id: UUID) -> None:
    get_container().actor_registry.add(
        Actor(
            actor_id=actor_id,
            legal_name="API Contract Test Actor",
            status=ActorStatus.ACTIVE,
            trust_level=TrustLevel.STANDARD,
        )
    )


def _bearer_header(actor_id: UUID) -> dict[str, str]:
    token = jwt.encode({"sub": str(actor_id)}, JWT_TEST_SECRET, algorithm=ALGORITHM)
    return {"Authorization": f"Bearer {token}"}


def test_api_declares_and_reads_derived_state(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_TEST_SECRET)
    get_container.cache_clear()
    actor_id = uuid4()
    _register_active_actor(actor_id)
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
                "actor_id": str(actor_id),
                "adapter_id": "api-test-adapter",
                "declared_at": now.isoformat(),
                "evidence": [],
            },
            "payload": {"attributes": []},
        },
        headers=_bearer_header(actor_id),
    )

    assert response.status_code == HTTP_CREATED

    state_response = client.get(
        f"/v1/custody/units/{unit_id}/state",
        params={"at": now.isoformat()},
    )

    assert state_response.status_code == HTTP_OK
    assert state_response.json()["state"]["event_type"] == CustodyEventType.MANUFACTURED.value


def test_api_rejects_invalid_precedence_without_history(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_TEST_SECRET)
    get_container.cache_clear()
    actor_id = uuid4()
    _register_active_actor(actor_id)
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
                "actor_id": str(actor_id),
                "adapter_id": "api-test-adapter",
                "declared_at": now.isoformat(),
            },
        },
        headers=_bearer_header(actor_id),
    )

    assert response.status_code == HTTP_UNPROCESSABLE_ENTITY


def test_api_rejects_declaration_from_unknown_actor(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_TEST_SECRET)
    get_container.cache_clear()
    client = TestClient(create_app())
    now = datetime(2026, 1, 1, tzinfo=UTC)
    unknown_actor_id = uuid4()

    response = client.post(
        "/v1/custody/assertions",
        json={
            "claim_id": str(uuid4()),
            "unit_id": "api-unauthorized-unit",
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
        headers=_bearer_header(unknown_actor_id),
    )

    assert response.status_code == HTTP_UNPROCESSABLE_ENTITY


def test_api_rejects_declaration_without_bearer_token(monkeypatch) -> None:
    """With HTTPBearer, requests carrying no Authorization header at all are
    rejected by FastAPI's scheme detection itself (403), distinct from a
    present-but-invalid token, which api/security.py rejects with 401.
    """

    monkeypatch.setenv("JWT_SECRET_KEY", JWT_TEST_SECRET)
    get_container.cache_clear()
    client = TestClient(create_app())
    now = datetime(2026, 1, 1, tzinfo=UTC)

    response = client.post(
        "/v1/custody/assertions",
        json={
            "claim_id": str(uuid4()),
            "unit_id": "api-no-token-unit",
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

    assert response.status_code == HTTP_FORBIDDEN


def test_api_ignores_body_actor_id_and_trusts_jwt_subject_only(monkeypatch) -> None:
    """The security fix under test: provenance.actor_id in the body must never
    be trusted for authorization — only the JWT's `sub` claim is authoritative.
    """

    monkeypatch.setenv("JWT_SECRET_KEY", JWT_TEST_SECRET)
    get_container.cache_clear()
    authenticated_actor_id = uuid4()
    impersonated_actor_id = uuid4()
    _register_active_actor(authenticated_actor_id)
    client = TestClient(create_app())
    now = datetime(2026, 1, 1, tzinfo=UTC)

    response = client.post(
        "/v1/custody/assertions",
        json={
            "claim_id": str(uuid4()),
            "unit_id": "api-jwt-override-unit",
            "event_type": CustodyEventType.MANUFACTURED.value,
            "occurred_at": now.isoformat(),
            "provenance": {
                "actor_id": str(impersonated_actor_id),
                "adapter_id": "api-test-adapter",
                "declared_at": now.isoformat(),
                "evidence": [],
            },
            "payload": {"attributes": []},
        },
        headers=_bearer_header(authenticated_actor_id),
    )

    assert response.status_code == HTTP_CREATED
    assert response.json()["assertion"]["provenance"]["actor_id"] == str(authenticated_actor_id)


def test_api_rate_limits_write_endpoint(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_TEST_SECRET)
    monkeypatch.setenv("RATE_LIMIT_WRITE_MAX_REQUESTS", "2")
    monkeypatch.setenv("RATE_LIMIT_WRITE_WINDOW_SECONDS", "60")
    get_container.cache_clear()
    get_write_rate_limiter.cache_clear()
    actor_id = uuid4()
    _register_active_actor(actor_id)
    client = TestClient(create_app())
    now = datetime(2026, 1, 1, tzinfo=UTC)

    try:

        def _declare(unit_id: str) -> object:
            return client.post(
                "/v1/custody/assertions",
                json={
                    "claim_id": str(uuid4()),
                    "unit_id": unit_id,
                    "event_type": CustodyEventType.MANUFACTURED.value,
                    "occurred_at": now.isoformat(),
                    "provenance": {
                        "actor_id": str(actor_id),
                        "adapter_id": "api-test-adapter",
                        "declared_at": now.isoformat(),
                        "evidence": [],
                    },
                    "payload": {"attributes": []},
                },
                headers=_bearer_header(actor_id),
            )

        first = _declare("rate-limit-unit-1")
        second = _declare("rate-limit-unit-2")
        third = _declare("rate-limit-unit-3")

        assert first.status_code == HTTP_CREATED
        assert second.status_code == HTTP_CREATED
        assert third.status_code == HTTP_TOO_MANY_REQUESTS
        assert "Retry-After" in third.headers
    finally:
        get_write_rate_limiter.cache_clear()
        monkeypatch.delenv("RATE_LIMIT_WRITE_MAX_REQUESTS", raising=False)
        monkeypatch.delenv("RATE_LIMIT_WRITE_WINDOW_SECONDS", raising=False)


def test_api_unit_reads_use_indexed_stream_not_full_log_scan(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_TEST_SECRET)
    get_container.cache_clear()
    actor_id = uuid4()
    _register_active_actor(actor_id)
    client = TestClient(create_app())
    now = datetime(2026, 1, 1, tzinfo=UTC)
    unit_id = "stream-not-scan-unit"

    response = client.post(
        "/v1/custody/assertions",
        json={
            "claim_id": str(uuid4()),
            "unit_id": unit_id,
            "event_type": CustodyEventType.MANUFACTURED.value,
            "occurred_at": now.isoformat(),
            "provenance": {
                "actor_id": str(actor_id),
                "adapter_id": "api-test-adapter",
                "declared_at": now.isoformat(),
                "evidence": [],
            },
            "payload": {"attributes": []},
        },
        headers=_bearer_header(actor_id),
    )
    assert response.status_code == HTTP_CREATED

    original_all = get_container().event_store.all

    def _forbid_full_scan() -> tuple[object, ...]:
        msg = "unit-scoped read must use stream(unit_id), not all()"
        raise AssertionError(msg)

    get_container().event_store.all = _forbid_full_scan  # type: ignore[method-assign]
    try:
        history_response = client.get(f"/v1/custody/units/{unit_id}/history")
        state_response = client.get(
            f"/v1/custody/units/{unit_id}/state", params={"at": now.isoformat()}
        )
    finally:
        get_container().event_store.all = original_all  # type: ignore[method-assign]

    assert history_response.status_code == HTTP_OK
    assert len(history_response.json()["assertions"]) == 1
    assert state_response.status_code == HTTP_OK
