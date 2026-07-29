"""FastAPI application factory for the Kernel API."""

from __future__ import annotations

from fastapi import FastAPI

from api.routes.custody import router as custody_router


def create_app() -> FastAPI:
    """Create the Kernel API application."""

    app = FastAPI(
        title="Medical Device Custody Kernel",
        version="0.1.0",
        description="Append-only API for verifiable medical-device custody claims.",
    )
    app.include_router(custody_router)
    return app


app = create_app()

