from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from kernel.custody.domain.assertions import CustodyAssertionDraft
from kernel.custody.domain.events import CustodyEventType, RejectionReason
from kernel.custody.domain.rejections import RejectedInconsistency
from kernel.custody.domain.value_objects import Provenance
from kernel.custody.infrastructure.sqlalchemy_event_store import (
    SqlAlchemyCustodyEventStore,
    SqlAlchemyRejectionLog,
)
from kernel.shared.infrastructure.database import Base, session_scope


def test_sqlalchemy_event_store_appends_and_reads_assertions() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        store = SqlAlchemyCustodyEventStore(session)
        draft = _draft(CustodyEventType.MANUFACTURED)

        committed = store.append(draft, expected_stream_version=0)
        session.commit()

        assert committed.global_position == 1
        assert store.by_claim_id(draft.claim_id) == committed
        assert store.stream(draft.unit_id) == (committed,)


def test_sqlalchemy_rejection_log_appends_rejections() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        log = SqlAlchemyRejectionLog(session)
        rejection = RejectedInconsistency(
            rejection_id=uuid4(),
            attempted_claim_id=uuid4(),
            unit_id="sql-rejected-unit",
            event_type=CustodyEventType.RECEIVED,
            reason=RejectionReason.PRECEDENCE_VIOLATION,
            detail="invalid transition",
            rejected_at=datetime(2026, 1, 1, tzinfo=UTC),
            provenance=_provenance(),
        )

        assert log.append(rejection) == rejection
        session.commit()
        assert log.all() == (rejection,)


def test_session_scope_commits_successful_work() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    draft = _draft(CustodyEventType.MANUFACTURED)

    with session_scope(factory) as session:
        store = SqlAlchemyCustodyEventStore(session)
        store.append(draft, expected_stream_version=0)

    with Session(engine) as session:
        store = SqlAlchemyCustodyEventStore(session)
        assert store.by_claim_id(draft.claim_id) is not None


def test_datetimes_round_trip_as_timezone_aware_utc() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        event_store = SqlAlchemyCustodyEventStore(session)
        rejection_log = SqlAlchemyRejectionLog(session)
        draft = _draft(CustodyEventType.MANUFACTURED)
        committed = event_store.append(draft, expected_stream_version=0)
        rejection = RejectedInconsistency(
            rejection_id=uuid4(),
            attempted_claim_id=uuid4(),
            unit_id=draft.unit_id,
            event_type=CustodyEventType.SHIPPED,
            reason=RejectionReason.PRECEDENCE_VIOLATION,
            detail="unit already manufactured",
            rejected_at=datetime(2026, 1, 1, tzinfo=UTC),
            provenance=draft.provenance,
        )
        rejection_log.append(rejection)
        session.commit()

        # expire_on_commit (default True) forces a fresh SELECT from SQLite on
        # the next access, exercising the real DB round trip.
        reread_assertion = event_store.by_claim_id(draft.claim_id)
        reread_rejection = rejection_log.all()[0]

    assert reread_assertion is not None
    assert reread_assertion.occurred_at.tzinfo is not None
    assert reread_assertion.occurred_at == committed.occurred_at
    assert reread_rejection.rejected_at.tzinfo is not None
    assert reread_rejection.rejected_at == rejection.rejected_at


def _draft(event_type: CustodyEventType) -> CustodyAssertionDraft:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    return CustodyAssertionDraft(
        claim_id=uuid4(),
        unit_id="sql-unit",
        event_type=event_type,
        occurred_at=now,
        provenance=_provenance(),
    )


def _provenance() -> Provenance:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    return Provenance(
        actor_id=uuid4(),
        adapter_id="sqlalchemy-test-adapter",
        declared_at=now,
    )
