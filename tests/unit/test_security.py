from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from api.security import ALGORITHM, get_current_actor_id

SECRET = "unit-test-secret"  # noqa: S105
HTTP_UNAUTHORIZED = 401


def _token(payload: dict[str, object], *, secret: str = SECRET) -> str:
    return jwt.encode(payload, secret, algorithm=ALGORITHM)


def _creds(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def test_valid_token_returns_actor_id(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", SECRET)
    actor_id = uuid4()

    result = get_current_actor_id(_creds(_token({"sub": str(actor_id)})))

    assert result == actor_id


def test_missing_secret_key_configuration_raises(monkeypatch) -> None:
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)

    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        get_current_actor_id(_creds(_token({"sub": str(uuid4())})))


def test_wrong_signature_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", SECRET)
    forged = _token({"sub": str(uuid4())}, secret="wrong-secret")  # noqa: S106

    with pytest.raises(HTTPException) as exc_info:
        get_current_actor_id(_creds(forged))

    assert exc_info.value.status_code == HTTP_UNAUTHORIZED


def test_expired_token_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", SECRET)
    expired = _token(
        {"sub": str(uuid4()), "exp": datetime.now(UTC) - timedelta(minutes=1)}
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_actor_id(_creds(expired))

    assert exc_info.value.status_code == HTTP_UNAUTHORIZED


def test_missing_sub_claim_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", SECRET)

    with pytest.raises(HTTPException) as exc_info:
        get_current_actor_id(_creds(_token({"role": "actor"})))

    assert exc_info.value.status_code == HTTP_UNAUTHORIZED


def test_non_uuid_sub_claim_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", SECRET)

    with pytest.raises(HTTPException) as exc_info:
        get_current_actor_id(_creds(_token({"sub": "not-a-uuid"})))

    assert exc_info.value.status_code == HTTP_UNAUTHORIZED


def test_malformed_token_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", SECRET)

    with pytest.raises(HTTPException) as exc_info:
        get_current_actor_id(_creds("not-a-jwt-at-all"))

    assert exc_info.value.status_code == HTTP_UNAUTHORIZED
