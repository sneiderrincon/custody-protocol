"""JWT bearer-token authentication for the Kernel API.

This module verifies bearer tokens issued by an external identity provider
and extracts the authenticated actor identity. It lives entirely in the API
layer: nothing in ``kernel/`` imports FastAPI, ``jwt``, or this module, so
Clean Architecture's dependency rule (domain/application never depend on
delivery-mechanism frameworks) is preserved.

Token *issuance* is intentionally out of scope here — see
docs/decisions/0010-jwt-authentication.md for why, and what identity
provider this API expects tokens from. There is no login endpoint; Swagger
UI's "Authorize" dialog accepts an already-issued bearer token directly
(HTTPBearer), rather than presenting a username/password form.

Diagnostics here are deliberately minimal: the bearer token and the shared
signing secret are credentials, so neither is ever logged, at any level.
Only the *class name* of a verification failure is emitted, at DEBUG.
"""

from __future__ import annotations

import logging
import os
from uuid import UUID

import jwt
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

ALGORITHM = "HS256"

_logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=True)
_BEARER_CREDENTIALS = Security(bearer_scheme)

_CREDENTIALS_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def _secret_key() -> str:
    """Return the shared secret used to verify JWT signatures.

    Read from the environment on every call (not cached at import time) so
    tests can set/unset it per case without import-order side effects.
    """

    secret = os.getenv("JWT_SECRET_KEY")
    if not secret:
        msg = "JWT_SECRET_KEY is not configured; refusing to verify tokens"
        raise RuntimeError(msg)
    return secret


def get_current_actor_id(
    credentials: HTTPAuthorizationCredentials = _BEARER_CREDENTIALS,
) -> UUID:
    """FastAPI dependency: verify the bearer JWT and return the actor_id.

    The token's ``sub`` claim is the only source of actor identity trusted by
    write endpoints. Any ``provenance.actor_id`` present in a request body is
    ignored for authorization purposes (see api/routes/custody.py) — this is
    exactly the trust boundary this dependency exists to enforce.
    """

    token = credentials.credentials
    try:
        payload = jwt.decode(token, _secret_key(), algorithms=[ALGORITHM])
    except jwt.InvalidTokenError as exc:
        _logger.debug("JWT rejected: %s", type(exc).__name__)
        raise _CREDENTIALS_ERROR from exc

    subject = payload.get("sub")
    if subject is None:
        _logger.debug("JWT rejected: missing 'sub' claim")
        raise _CREDENTIALS_ERROR
    try:
        return UUID(str(subject))
    except ValueError as exc:
        _logger.debug("JWT rejected: 'sub' claim is not a UUID")
        raise _CREDENTIALS_ERROR from exc
