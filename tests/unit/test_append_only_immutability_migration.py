from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

from alembic.operations import Operations
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, inspect

_MIGRATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "alembic"
    / "versions"
    / "0002_enforce_append_only_immutability.py"
)


def _load_migration_module() -> ModuleType:
    """Import the migration file directly.

    Alembic revision filenames start with digits and are not valid Python
    module paths, so they cannot be `import`ed normally.
    """

    spec = importlib.util.spec_from_file_location(
        "migration_0002_enforce_append_only_immutability", _MIGRATION_PATH
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


migration = _load_migration_module()


def test_is_postgresql_true_for_postgresql_dialect() -> None:
    assert migration._is_postgresql("postgresql") is True


def test_is_postgresql_false_for_sqlite_dialect() -> None:
    assert migration._is_postgresql("sqlite") is False


def test_upgrade_is_a_safe_no_op_on_sqlite() -> None:
    """Runs the real migration `upgrade()`/`downgrade()` functions (not just the
    pure dialect check) against a live SQLite connection, proving
    `alembic upgrade head` does not break local development, where SQLite is
    used (ADR 0006/0012). This does NOT prove the PostgreSQL REVOKE/GRANT
    behavior works — that requires a real PostgreSQL instance, which this
    environment does not have (see docs/decisions/0013-append-only-db-enforcement.md).
    """

    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as connection:
        # Migration 0001 must run first so the tables this migration targets
        # exist -- exercising the real upgrade/downgrade path end to end.
        migration_0001 = importlib.util.spec_from_file_location(
            "migration_0001_create_kernel_event_logs",
            _MIGRATION_PATH.parent / "0001_create_kernel_event_logs.py",
        )
        assert migration_0001 is not None
        assert migration_0001.loader is not None
        module_0001 = importlib.util.module_from_spec(migration_0001)
        migration_0001.loader.exec_module(module_0001)

        context = MigrationContext.configure(connection)
        with Operations.context(context):
            module_0001.upgrade()
            migration.upgrade()  # must not raise on SQLite
            migration.downgrade()  # must not raise on SQLite

        inspector = inspect(connection)
        assert "custody_assertions" in inspector.get_table_names()
        assert "rejected_inconsistencies" in inspector.get_table_names()
