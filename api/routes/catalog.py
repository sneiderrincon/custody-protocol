"""FastAPI routes for device catalog commands and queries."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict

from api.dependencies import KernelContainer, get_container
from api.rate_limit import enforce_write_rate_limit
from api.security import get_current_actor_id
from kernel.catalog.application.commands import RegisterCanonicalDevice
from kernel.catalog.domain.device import CanonicalDevice
from kernel.catalog.domain.errors import DeviceNotFoundError, DuplicateUdiDiError

router = APIRouter(prefix="/v1/catalog", tags=["catalog"])
CONTAINER_DEPENDENCY = Depends(get_container)
ACTOR_DEPENDENCY = Depends(get_current_actor_id)
RATE_LIMIT_DEPENDENCY = Depends(enforce_write_rate_limit)


class DeviceResponse(BaseModel):
    """API response for a canonical device."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    device: CanonicalDevice


@router.post(
    "/devices",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_device(
    command: RegisterCanonicalDevice,
    container: KernelContainer = CONTAINER_DEPENDENCY,
    _authenticated_actor_id: UUID = ACTOR_DEPENDENCY,
    _rate_limit: None = RATE_LIMIT_DEPENDENCY,
) -> DeviceResponse:
    """Register a new canonical device. Requires authentication (any known actor).

    Fine-grained authorization (a MANAGE_CATALOG permission restricted to
    Manufacturer-role organizations) is deferred to the Organization/Identity
    increment -- see docs/decisions/0015-device-catalog.md. For now this
    endpoint requires the same authentication as custody writes, not yet
    role-scoped.
    """

    try:
        device = container.catalog_service.register(command)
    except DuplicateUdiDiError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return DeviceResponse(device=device)


@router.get("/devices/{device_id}", response_model=DeviceResponse)
def get_device(
    device_id: UUID,
    container: KernelContainer = CONTAINER_DEPENDENCY,
) -> DeviceResponse:
    """Return a canonical device by its internal identifier."""

    try:
        device = container.catalog_service.get(device_id)
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return DeviceResponse(device=device)


@router.get("/devices", response_model=DeviceResponse)
def find_device_by_udi_di(
    udi_di: str = Query(min_length=1),
    container: KernelContainer = CONTAINER_DEPENDENCY,
) -> DeviceResponse:
    """Return a canonical device by its UDI-DI."""

    device: CanonicalDevice | None = container.catalog_service.find_by_udi_di(udi_di)
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no catalog entry for UDI-DI {udi_di}",
        )
    return DeviceResponse(device=device)
