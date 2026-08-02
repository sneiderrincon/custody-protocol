from __future__ import annotations

from uuid import uuid4

import jwt
from fastapi.testclient import TestClient

from api.dependencies import get_container
from api.main import create_app
from api.security import ALGORITHM
from kernel.identity.domain.actors import Actor, ActorStatus, TrustLevel

HTTP_OK = 200
HTTP_CREATED = 201
HTTP_CONFLICT = 409
HTTP_NOT_FOUND = 404
HTTP_FORBIDDEN = 403

JWT_TEST_SECRET = "test-secret-do-not-use-in-production"  # noqa: S105


def _register_active_actor(actor_id) -> None:
    get_container().actor_registry.add(
        Actor(
            actor_id=actor_id,
            legal_name="Catalog API Test Actor",
            status=ActorStatus.ACTIVE,
            trust_level=TrustLevel.STANDARD,
        )
    )


def _bearer_header(actor_id) -> dict[str, str]:
    token = jwt.encode({"sub": str(actor_id)}, JWT_TEST_SECRET, algorithm=ALGORITHM)
    return {"Authorization": f"Bearer {token}"}


def _device_payload(udi_di_value: str) -> dict[str, object]:
    return {
        "udi_di": {"value": udi_di_value, "issuing_agency": "GS1"},
        "generic_regulatory_name": "External Fixation Screw",
        "manufacturer": {"legal_name": "Acme Medical S.A.S."},
        "manufacturer_model_reference": "AFX-100",
        "gmdn": {"code": "12345", "term": "Bone screw, non-bioabsorbable"},
        "risk_class": "IIb",
        "packaging": {"levels": [{"unit": "each", "quantity": 1}]},
        "unit_of_measure": "unit",
        "minimum_consumption_unit": "unit",
        "storage_conditions": {"light_sensitive": False},
        "sterilization": {"is_sterile": True, "method": "ethylene_oxide"},
        "commercial_presentation": "Individually packaged, sterile",
    }


def test_register_device_requires_authentication(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_TEST_SECRET)
    get_container.cache_clear()
    client = TestClient(create_app())

    response = client.post("/v1/catalog/devices", json=_device_payload("UDI-DI:API-NOAUTH"))

    assert response.status_code == HTTP_FORBIDDEN


def test_register_and_fetch_device_by_id_and_udi_di(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_TEST_SECRET)
    get_container.cache_clear()
    actor_id = uuid4()
    _register_active_actor(actor_id)
    client = TestClient(create_app())

    create_response = client.post(
        "/v1/catalog/devices",
        json=_device_payload("UDI-DI:API-REG-001"),
        headers=_bearer_header(actor_id),
    )
    assert create_response.status_code == HTTP_CREATED
    device_id = create_response.json()["device"]["device_id"]

    by_id_response = client.get(f"/v1/catalog/devices/{device_id}")
    by_udi_di_response = client.get(
        "/v1/catalog/devices", params={"udi_di": "UDI-DI:API-REG-001"}
    )

    assert by_id_response.status_code == HTTP_OK
    assert by_udi_di_response.status_code == HTTP_OK
    assert by_id_response.json()["device"]["device_id"] == device_id
    assert by_udi_di_response.json()["device"]["device_id"] == device_id


def test_register_device_rejects_duplicate_udi_di(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_TEST_SECRET)
    get_container.cache_clear()
    actor_id = uuid4()
    _register_active_actor(actor_id)
    client = TestClient(create_app())
    headers = _bearer_header(actor_id)

    first = client.post(
        "/v1/catalog/devices", json=_device_payload("UDI-DI:API-DUP"), headers=headers
    )
    second = client.post(
        "/v1/catalog/devices", json=_device_payload("UDI-DI:API-DUP"), headers=headers
    )

    assert first.status_code == HTTP_CREATED
    assert second.status_code == HTTP_CONFLICT


def test_get_unknown_device_returns_404(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_TEST_SECRET)
    get_container.cache_clear()
    client = TestClient(create_app())

    response = client.get(f"/v1/catalog/devices/{uuid4()}")

    assert response.status_code == HTTP_NOT_FOUND


def test_find_by_unknown_udi_di_returns_404(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_TEST_SECRET)
    get_container.cache_clear()
    client = TestClient(create_app())

    response = client.get("/v1/catalog/devices", params={"udi_di": "UDI-DI:DOES-NOT-EXIST"})

    assert response.status_code == HTTP_NOT_FOUND
