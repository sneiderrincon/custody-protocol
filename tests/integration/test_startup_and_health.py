from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from api.dependencies import get_container
from api.main import create_app
from kernel.shared.infrastructure.database import Base

HTTP_OK = 200
HTTP_SERVICE_UNAVAILABLE = 503

JWT_TEST_SECRET = "test-secret-do-not-use-in-production"  # noqa: S105


def test_startup_fails_fast_without_jwt_secret_key(monkeypatch) -> None:
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    get_container.cache_clear()

    # Starlette's TestClient runs lifespan startup on __enter__ and re-raises
    # whatever the startup hook raised, proving misconfiguration fails the
    # process before it ever serves a request (fail fast).
    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"), TestClient(create_app()):
        pass


def test_startup_succeeds_with_valid_configuration(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_TEST_SECRET)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    get_container.cache_clear()

    with TestClient(create_app()) as client:
        response = client.get("/healthz")

    assert response.status_code == HTTP_OK
    assert response.json() == {"status": "ok"}


def test_startup_pings_database_when_configured(monkeypatch, tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'startup.db'}"
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_TEST_SECRET)
    monkeypatch.setenv("DATABASE_URL", database_url)
    get_container.cache_clear()

    try:
        with TestClient(create_app()) as client:
            response = client.get("/healthz")

        assert response.status_code == HTTP_OK
    finally:
        get_container.cache_clear()
        monkeypatch.delenv("DATABASE_URL", raising=False)


def test_healthz_reports_ok_without_authentication(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_TEST_SECRET)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    get_container.cache_clear()
    client = TestClient(create_app())

    response = client.get("/healthz")

    assert response.status_code == HTTP_OK
    assert response.json() == {"status": "ok"}


def test_healthz_reports_unhealthy_when_database_unreachable(monkeypatch, tmp_path) -> None:
    unreachable_db = tmp_path / "does-not-exist" / "unreachable.db"
    monkeypatch.setenv("JWT_SECRET_KEY", JWT_TEST_SECRET)
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{unreachable_db}")
    get_container.cache_clear()
    client = TestClient(create_app())

    try:
        response = client.get("/healthz")

        assert response.status_code == HTTP_SERVICE_UNAVAILABLE
    finally:
        get_container.cache_clear()
        monkeypatch.delenv("DATABASE_URL", raising=False)
