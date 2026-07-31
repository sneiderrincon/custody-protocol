"""Health/readiness endpoint.

Used by Docker's HEALTHCHECK instruction and by orchestrators (Kubernetes
liveness/readiness probes, load balancers). Deliberately not behind
authentication (ADR 0010 scoped auth to write endpoints only) — health
checks are an operational concern, not custody data.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import KernelContainer, get_container

router = APIRouter(tags=["health"])
CONTAINER_DEPENDENCY = Depends(get_container)


@router.get("/healthz")
def healthz(container: KernelContainer = CONTAINER_DEPENDENCY) -> dict[str, str]:
    """Report whether the process and its backing store are reachable."""

    try:
        container.ping()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="unhealthy",
        ) from exc
    return {"status": "ok"}
