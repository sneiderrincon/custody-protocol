"""Enforce append-only immutability at the database level.

Root cause this addresses: `custody_assertions`/`rejected_inconsistencies` had no
UPDATE/DELETE at the ORM level (the CustodyEventStore/RejectionLog ports expose no
such methods), but nothing at the database itself prevented a direct UPDATE or
DELETE — immutability was a code convention only, not a database guarantee. A
regulated custody log should not depend solely on "nobody wrote that code".

Revision ID: 0002_enforce_append_only_immutability
Revises: 0001_create_kernel_event_logs
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0002_enforce_append_only_immutability"
down_revision: str | None = "0001_create_kernel_event_logs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_IMMUTABLE_TABLES = ("custody_assertions", "rejected_inconsistencies")


def _is_postgresql(dialect_name: str) -> bool:
    """True when `dialect_name` is PostgreSQL.

    PostgreSQL's role-based GRANT/REVOKE model is what makes this migration's
    enforcement possible. SQLite — the dialect used for local development and
    this repo's test suite (ADR 0006/0012) — has no privilege system and does
    not support REVOKE/GRANT syntax at all, so this migration must be a no-op
    there rather than fail `alembic upgrade head` for local development.
    """

    return dialect_name == "postgresql"


def upgrade() -> None:
    """Revoke UPDATE/DELETE on the append-only logs, even from the owning role.

    PostgreSQL table owners keep implicit GRANT authority after revoking their
    own DML privileges (they can always re-grant it back to themselves), so
    this does not lock anyone out permanently — it removes the *default*
    ability to mutate or delete committed rows, closing the gap between "the
    application code never issues UPDATE/DELETE" and "the database physically
    prevents it", including for a compromised process using the same
    credentials as the application.
    """

    bind = op.get_bind()
    if not _is_postgresql(bind.dialect.name):
        return
    for table in _IMMUTABLE_TABLES:
        op.execute(f"REVOKE UPDATE, DELETE ON {table} FROM CURRENT_USER")


def downgrade() -> None:
    """Restore UPDATE/DELETE privileges (reverses `upgrade`)."""

    bind = op.get_bind()
    if not _is_postgresql(bind.dialect.name):
        return
    for table in _IMMUTABLE_TABLES:
        op.execute(f"GRANT UPDATE, DELETE ON {table} TO CURRENT_USER")
