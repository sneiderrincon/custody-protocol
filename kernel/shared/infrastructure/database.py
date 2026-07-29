"""Database infrastructure helpers."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM mappings."""


def build_engine(database_url: str) -> Engine:
    """Create a SQLAlchemy engine for the kernel database."""

    return create_engine(database_url, future=True)


def build_session_factory(database_url: str) -> sessionmaker[Session]:
    """Create a session factory bound to the configured database."""

    return sessionmaker(bind=build_engine(database_url), expire_on_commit=False)


@contextmanager
def session_scope(factory: sessionmaker[Session]) -> Iterator[Session]:
    """Yield a transactional session and commit or roll back around it."""

    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
