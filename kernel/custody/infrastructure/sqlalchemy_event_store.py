"""SQLAlchemy implementation of custody event-store ports."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from kernel.custody.domain.assertions import CommittedCustodyAssertion, CustodyAssertionDraft
from kernel.custody.domain.events import CustodyEventType, RejectionReason
from kernel.custody.domain.rejections import RejectedInconsistency
from kernel.custody.domain.value_objects import AssertionPayload, Provenance
from kernel.custody.infrastructure.sqlalchemy_models import (
    CustodyAssertionRecord,
    RejectedInconsistencyRecord,
)
from kernel.shared.domain.errors import ConcurrencyConflictError, IdempotencyConflictError


class SqlAlchemyCustodyEventStore:
    """PostgreSQL-backed append-only event store for custody assertions."""

    def __init__(self, session: Session) -> None:
        """Initialize the store with a SQLAlchemy session."""

        self._session = session

    def stream(self, unit_id: str) -> tuple[CommittedCustodyAssertion, ...]:
        """Return a unit stream ordered by stream version."""

        statement = (
            select(CustodyAssertionRecord)
            .where(CustodyAssertionRecord.unit_id == unit_id)
            .order_by(CustodyAssertionRecord.stream_version)
        )
        return tuple(_record_to_assertion(record) for record in self._session.scalars(statement))

    def append(
        self,
        draft: CustodyAssertionDraft,
        *,
        expected_stream_version: int,
    ) -> CommittedCustodyAssertion:
        """Append a custody assertion with idempotency and optimistic stream checks."""

        existing = self.by_claim_id(draft.claim_id)
        if existing is not None:
            if existing.matches_draft(draft):
                return existing
            msg = f"claim_id {draft.claim_id} was reused for different assertion content"
            raise IdempotencyConflictError(msg)

        current_version = self._current_stream_version(draft.unit_id)
        if current_version != expected_stream_version:
            msg = (
                f"expected stream version {expected_stream_version}, "
                f"found {current_version} for unit {draft.unit_id}"
            )
            raise ConcurrencyConflictError(msg)

        record = CustodyAssertionRecord(
            stream_version=current_version + 1,
            claim_id=str(draft.claim_id),
            unit_id=draft.unit_id,
            event_type=draft.event_type.value,
            occurred_at=draft.occurred_at,
            provenance=draft.provenance.model_dump(mode="json"),
            payload=draft.payload.model_dump(mode="json"),
        )
        self._session.add(record)
        try:
            self._session.flush()
        except IntegrityError as exc:
            msg = "concurrent append violated custody event-store constraints"
            raise ConcurrencyConflictError(msg) from exc
        return _record_to_assertion(record)

    def by_claim_id(self, claim_id: UUID) -> CommittedCustodyAssertion | None:
        """Return an assertion by claim id."""

        statement = select(CustodyAssertionRecord).where(
            CustodyAssertionRecord.claim_id == str(claim_id)
        )
        record = self._session.scalars(statement).one_or_none()
        if record is None:
            return None
        return _record_to_assertion(record)

    def all(self) -> tuple[CommittedCustodyAssertion, ...]:
        """Return the global custody log in append order."""

        statement = select(CustodyAssertionRecord).order_by(CustodyAssertionRecord.global_position)
        return tuple(_record_to_assertion(record) for record in self._session.scalars(statement))

    def _current_stream_version(self, unit_id: str) -> int:
        statement: Select[tuple[int]] = select(
            func.max(CustodyAssertionRecord.stream_version)
        ).where(CustodyAssertionRecord.unit_id == unit_id)
        return self._session.execute(statement).scalar_one() or 0


class SqlAlchemyRejectionLog:
    """PostgreSQL-backed append-only rejection log."""

    def __init__(self, session: Session) -> None:
        """Initialize the log with a SQLAlchemy session."""

        self._session = session

    def append(self, rejection: RejectedInconsistency) -> RejectedInconsistency:
        """Append a rejected inconsistency event."""

        record = RejectedInconsistencyRecord(
            rejection_id=str(rejection.rejection_id),
            attempted_claim_id=str(rejection.attempted_claim_id),
            unit_id=rejection.unit_id,
            event_type=rejection.event_type.value,
            reason=rejection.reason.value,
            detail=rejection.detail,
            rejected_at=rejection.rejected_at,
            provenance=rejection.provenance.model_dump(mode="json"),
        )
        self._session.add(record)
        self._session.flush()
        return rejection

    def all(self) -> tuple[RejectedInconsistency, ...]:
        """Return all rejection events in append order."""

        statement = select(RejectedInconsistencyRecord).order_by(
            RejectedInconsistencyRecord.global_position
        )
        return tuple(_record_to_rejection(record) for record in self._session.scalars(statement))


def _as_utc(value: datetime) -> datetime:
    """Return ``value`` as a timezone-aware UTC datetime.

    SQLite has no native timezone-aware timestamp type: SQLAlchemy's
    ``DateTime(timezone=True)`` maps to PostgreSQL's ``TIMESTAMPTZ`` (which
    round-trips tz-aware values correctly), but on SQLite it falls back to a
    naive ``DATETIME``, silently dropping ``tzinfo`` on read even though it
    was present on write. Domain writes always store UTC-normalized values,
    so a naive value read back is known to already represent UTC — we only
    reattach the tzinfo, never reinterpret the wall-clock value. On
    PostgreSQL, ``value`` already carries tzinfo, so this is a no-op there.
    """

    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _record_to_assertion(record: CustodyAssertionRecord) -> CommittedCustodyAssertion:
    return CommittedCustodyAssertion(
        claim_id=UUID(record.claim_id),
        unit_id=record.unit_id,
        event_type=CustodyEventType(record.event_type),
        occurred_at=_as_utc(record.occurred_at),
        provenance=Provenance.model_validate(record.provenance),
        payload=AssertionPayload.model_validate(record.payload),
        global_position=record.global_position,
        stream_version=record.stream_version,
    )


def _record_to_rejection(record: RejectedInconsistencyRecord) -> RejectedInconsistency:
    return RejectedInconsistency(
        rejection_id=UUID(record.rejection_id),
        attempted_claim_id=UUID(record.attempted_claim_id),
        unit_id=record.unit_id,
        event_type=CustodyEventType(record.event_type),
        reason=RejectionReason(record.reason),
        detail=record.detail,
        rejected_at=_as_utc(record.rejected_at),
        provenance=Provenance.model_validate(record.provenance),
    )
