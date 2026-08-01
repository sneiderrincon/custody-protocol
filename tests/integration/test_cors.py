from __future__ import annotations

from fastapi.testclient import TestClient

from api.dependencies import get_container
from api.main import create_app

JWT_TEST_SECRET = "test-secret-do-not-use-in-production"  # noqa: S105


def test_cors_headers_absent_by_default(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_TEST_SECRET)
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)
    get_container.cache_clear()
    client = TestClient(create_app())

    response = client.get("/healthz", headers={"Origin": "http://localhost:5500"})

    assert "access-control-allow-origin" not in {k.lower() for k in response.headers}


def test_cors_headers_present_for_configured_origin(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_TEST_SECRET)
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "http://localhost:5500")
    get_container.cache_clear()

    try:
        client = TestClient(create_app())

        response = client.get("/healthz", headers={"Origin": "http://localhost:5500"})

        assert response.headers.get("access-control-allow-origin") == "http://localhost:5500"
    finally:
        monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)


def test_cors_rejects_unlisted_origin(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_TEST_SECRET)
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "http://localhost:5500")
    get_container.cache_clear()

    try:
        client = TestClient(create_app())

        response = client.get("/healthz", headers={"Origin": "http://evil.example"})

        assert "access-control-allow-origin" not in {k.lower() for k in response.headers}
    finally:
        monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)


def test_cors_supports_multiple_comma_separated_origins(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_TEST_SECRET)
    monkeypatch.setenv(
        "CORS_ALLOWED_ORIGINS", "http://localhost:5500, http://localhost:3000"
    )
    get_container.cache_clear()

    try:
        client = TestClient(create_app())

        first = client.get("/healthz", headers={"Origin": "http://localhost:5500"})
        second = client.get("/healthz", headers={"Origin": "http://localhost:3000"})

        assert first.headers.get("access-control-allow-origin") == "http://localhost:5500"
        assert second.headers.get("access-control-allow-origin") == "http://localhost:3000"
    finally:
        monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)
