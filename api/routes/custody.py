"""FastAPI routes for custody commands and queries."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict

from api.dependencies import KernelContainer, get_container
from kernel.custody.application.commands import DeclareCustodyAssertion
from kernel.custody.application.projections import CustodyProjectionEngine, CustodyStateProjection
from kernel.custody.domain.assertions import CommittedCustodyAssertion
from kernel.custody.domain.rules import RuleViolationError
from kernel.governance.domain.policies import GovernancePolicyViolationError
from kernel.shared.domain.errors import ConcurrencyConflictError, IdempotencyConflictError

router = APIRouter(prefix="/v1/custody", tags=["custody"])
CONTAINER_DEPENDENCY = Depends(get_container)


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
) -> AssertionResponse:
    """Declare a custody assertion through the write model."""

    try:
        assertion = container.declare_service.handle(command)
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
    return HistoryResponse(assertions=projection.history(unit_id, container.event_store.all()))


@router.get("/units/{unit_id}/state", response_model=StateResponse)
def unit_state(
    unit_id: str,
    at: datetime,
    container: KernelContainer = CONTAINER_DEPENDENCY,
) -> StateResponse:
    """Return derived unit state at a domain timestamp."""

    projection = CustodyProjectionEngine()
    return StateResponse(state=projection.state_at(unit_id, at, container.event_store.all()))


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
