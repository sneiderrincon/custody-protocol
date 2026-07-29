"""Custody domain event vocabulary."""

from __future__ import annotations

from enum import StrEnum


class CustodyEventType(StrEnum):
    """Closed event set for physical medical-device custody facts."""

    MANUFACTURED = "Fabricado"
    SHIPPED = "Enviado"
    RECEIVED = "Recibido"
    DISPATCHED = "Despachado"
    USED_IMPLANTED = "UsadoImplantado"
    RETURNED = "Devuelto"
    DECOMMISSIONED = "DadoDeBaja"
    INITIAL_STATE_DECLARED = "EstadoInicialDeclarado"


class RejectionReason(StrEnum):
    """Reasons for rejecting attempted custody assertions."""

    GOVERNANCE_VIOLATION = "governance_violation"
    PRECEDENCE_VIOLATION = "precedence_violation"
    TEMPORAL_VIOLATION = "temporal_violation"
    IDEMPOTENCY_CONFLICT = "idempotency_conflict"
    CONCURRENCY_CONFLICT = "concurrency_conflict"
