"""Versioned custody rule engine."""

from __future__ import annotations

from dataclasses import dataclass

from kernel.custody.domain.assertions import CommittedCustodyAssertion, CustodyAssertionDraft
from kernel.custody.domain.events import CustodyEventType
from kernel.shared.domain.errors import DomainError


class RuleViolationError(DomainError):
    """Raised when a custody assertion violates a domain rule."""


@dataclass(frozen=True, slots=True)
class VersionedCustodyRuleEngine:
    """Small, explicit rule engine for custody consistency.

    This is deliberately code-versioned domain logic, not a customer-configurable rules
    product. Rule changes are kernel releases.
    """

    version: str = "custody-rules/v1"

    _allowed_after: dict[CustodyEventType, frozenset[CustodyEventType]] | None = None

    def __post_init__(self) -> None:
        if self._allowed_after is None:
            object.__setattr__(self, "_allowed_after", _DEFAULT_ALLOWED_AFTER)

    def validate(
        self,
        draft: CustodyAssertionDraft,
        history: tuple[CommittedCustodyAssertion, ...],
    ) -> None:
        self._validate_temporal_consistency(draft, history)
        self._validate_precedence(draft, history)

    def _validate_temporal_consistency(
        self,
        draft: CustodyAssertionDraft,
        history: tuple[CommittedCustodyAssertion, ...],
    ) -> None:
        if not history:
            return
        latest = history[-1]
        if draft.occurred_at < latest.occurred_at:
            msg = (
                f"{draft.event_type} occurred at {draft.occurred_at.isoformat()} before "
                f"latest event {latest.event_type} at {latest.occurred_at.isoformat()}"
            )
            raise RuleViolationError(msg)

    def _validate_precedence(
        self,
        draft: CustodyAssertionDraft,
        history: tuple[CommittedCustodyAssertion, ...],
    ) -> None:
        if not history:
            if draft.event_type in _INITIAL_EVENTS:
                return
            msg = f"{draft.event_type} cannot start a custody stream"
            raise RuleViolationError(msg)

        previous = history[-1].event_type
        allowed = self._allowed_after or _DEFAULT_ALLOWED_AFTER
        if draft.event_type not in allowed[previous]:
            msg = f"{draft.event_type} cannot follow {previous}"
            raise RuleViolationError(msg)


_INITIAL_EVENTS = frozenset(
    {
        CustodyEventType.INITIAL_STATE_DECLARED,
        CustodyEventType.MANUFACTURED,
    }
)

_DEFAULT_ALLOWED_AFTER = {
    CustodyEventType.INITIAL_STATE_DECLARED: frozenset(
        {
            CustodyEventType.MANUFACTURED,
            CustodyEventType.SHIPPED,
            CustodyEventType.RECEIVED,
            CustodyEventType.DECOMMISSIONED,
        }
    ),
    CustodyEventType.MANUFACTURED: frozenset(
        {
            CustodyEventType.SHIPPED,
            CustodyEventType.DECOMMISSIONED,
        }
    ),
    CustodyEventType.SHIPPED: frozenset(
        {
            CustodyEventType.RECEIVED,
            CustodyEventType.RETURNED,
        }
    ),
    CustodyEventType.RECEIVED: frozenset(
        {
            CustodyEventType.DISPATCHED,
            CustodyEventType.RETURNED,
            CustodyEventType.DECOMMISSIONED,
        }
    ),
    CustodyEventType.DISPATCHED: frozenset(
        {
            CustodyEventType.USED_IMPLANTED,
            CustodyEventType.RETURNED,
        }
    ),
    CustodyEventType.USED_IMPLANTED: frozenset({CustodyEventType.DECOMMISSIONED}),
    CustodyEventType.RETURNED: frozenset(
        {
            CustodyEventType.SHIPPED,
            CustodyEventType.DECOMMISSIONED,
        }
    ),
    CustodyEventType.DECOMMISSIONED: frozenset(),
}

