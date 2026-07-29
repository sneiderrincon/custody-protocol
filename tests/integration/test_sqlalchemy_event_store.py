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
