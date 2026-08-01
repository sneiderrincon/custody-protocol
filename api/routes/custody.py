"""FastAPI routes for custody commands and queries."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict

from api.dependencies import KernelContainer, get_container
from api.rate_limit import enforce_write_rate_limit
from api.security import get_current_actor_id
from kernel.custody.application.commands import DeclareCustodyAssertion
from kernel.custody.application.projections import CustodyProjectionEngine, CustodyStateProjection
from kernel.custody.domain.assertions import CommittedCustodyAssertion
from kernel.custody.domain.rules import RuleViolationError
from kernel.governance.domain.policies import GovernancePolicyViolationError
from kernel.shared.domain.errors import ConcurrencyConflictError, IdempotencyConflictError

router = APIRouter(prefix="/v1/custody", tags=["custody"])
CONTAINER_DEPENDENCY = Depends(get_container)
ACTOR_DEPENDENCY = Depends(get_current_actor_id)
RATE_LIMIT_DEPENDENCY = Depends(enforce_write_rate_limit)


class AssertionResponse(BaseModel):
    """API response for a committed custody assertion."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    assertion: CommittedCustodyAssertion


class HistoryResponse(BaseModel):
    """API response for a unit history query."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    assertions: tuple[CommittedCustodyAssertion, ...]


class StateResponse(BaseModel):
    """API response for a derived state query."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    state: CustodyStateProjection


@router.post(
    "/assertions",
    response_model=AssertionResponse,
    status_code=status.HTTP_201_CREATED,
)
def declare_assertion(
    command: DeclareCustodyAssertion,
    container: KernelContainer = CONTAINER_DEPENDENCY,
    authenticated_actor_id: UUID = ACTOR_DEPENDENCY,
    _rate_limit: None = RATE_LIMIT_DEPENDENCY,
) -> AssertionResponse:
    """Declare a custody assertion through the write model.

    The authenticated actor_id (from the verified JWT) always overrides
    whatever actor_id is present in the request body's provenance — a
    client-supplied actor_id is never trusted for authorization. The request
    schema is unchanged for backward compatibility; the field is simply no
    longer authoritative.
    """

    authenticated_command = command.model_copy(
        update={
            "provenance": command.provenance.model_copy(
                update={"actor_id": authenticated_actor_id}
            )
        }
    )
    try:
        assertion = container.declare_service.handle(authenticated_command)
    except (GovernancePolicyViolationError, RuleViolationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except (ConcurrencyConflictError, IdempotencyConflictError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return AssertionResponse(assertion=assertion)


@router.get("/units/{unit_id}/history", response_model=HistoryResponse)
def unit_history(
    unit_id: str,
    container: KernelContainer = CONTAINER_DEPENDENCY,
) -> HistoryResponse:
    """Return a derived unit history from the read model."""

    projection = CustodyProjectionEngine()
    return HistoryResponse(
        assertions=projection.history(unit_id, container.event_store.stream(unit_id))
    )


@router.get("/units/{unit_id}/state", response_model=StateResponse)
def unit_state(
    unit_id: str,
    at: datetime,
    container: KernelContainer = CONTAINER_DEPENDENCY,
) -> StateResponse:
    """Return derived unit state at a domain timestamp."""

    projection = CustodyProjectionEngine()
    return StateResponse(
        state=projection.state_at(unit_id, at, container.event_store.stream(unit_id))
    )


@router.get("/assertions/{claim_id}", response_model=AssertionResponse)
def assertion_by_claim(
    claim_id: UUID,
    container: KernelContainer = CONTAINER_DEPENDENCY,
) -> AssertionResponse:
    """Return one assertion for provenance verification."""

    assertion = container.event_store.by_claim_id(claim_id)
    if assertion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="assertion not found")
    return AssertionResponse(assertion=assertion)
