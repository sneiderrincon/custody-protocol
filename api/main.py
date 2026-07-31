"""FastAPI application factory for the Kernel API."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.dependencies import get_container
from api.routes.custody import router as custody_router
from api.routes.health import router as health_router


def _validate_startup_configuration() -> None:
    """Fail fast on misconfiguration instead of surfacing it on first request.

    Runs once at process startup (see `_lifespan` below), so a bad
    deployment exits immediately with a clear error -- visible in
    `docker compose up` logs and via the process exit code -- rather than
    passing a Docker HEALTHCHECK only to 500 on the first real request.
    """

    if not os.getenv("JWT_SECRET_KEY"):
        msg = "JWT_SECRET_KEY is not configured; the API cannot authenticate requests"
        raise RuntimeError(msg)
    # DATABASE_URL is optional by design (ADR 0006's in-memory fallback is a
    # valid configuration for local development), so its absence is not an
    # error here. When it is set, ping() proves the database is reachable --
    # migrations are expected to have already run (see docker-entrypoint.sh).
    get_container().ping()


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
    _validate_startup_configuration()
    yield


def create_app() -> FastAPI:
    """Create the Kernel API application."""

    app = FastAPI(
        title="Medical Device Custody Kernel",
        version="0.1.0",
        description="Append-only API for verifiable medical-device custody claims.",
        lifespan=_lifespan,
    )
    app.include_router(custody_router)
    app.include_router(health_router)
    return app


app = create_app()
