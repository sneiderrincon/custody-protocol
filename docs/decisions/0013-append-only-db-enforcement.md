# ADR 0013: Append-Only Immutability Enforced at the Database Level (PostgreSQL)

## Status

Accepted.

## Context

`custody_assertions`/`rejected_inconsistencies` had no UPDATE/DELETE at the ORM
level — `CustodyEventStore`/`RejectionLog` (the ports) expose no such methods, and
no code in this repository issues them. But nothing at the database itself
prevented a direct `UPDATE`/`DELETE` — via a different tool, a future bug, or a
compromised process reusing the application's own database credentials.
Immutability was a code convention, not a database guarantee, which is not a
sufficient bar for a regulated custody log.

## Decision

Migration `0002_enforce_append_only_immutability` runs
`REVOKE UPDATE, DELETE ON custody_assertions, rejected_inconsistencies FROM
CURRENT_USER` against PostgreSQL. `CURRENT_USER` (not a hardcoded role name like
`kernel`) is used so this works regardless of which role the connecting
credentials happen to use in a given environment. PostgreSQL table owners retain
implicit `GRANT` authority even after revoking their own DML privileges, so this
is reversible (see `downgrade()`) and does not lock anyone out permanently — it
removes the *default* ability to mutate or delete committed rows for the
application's normal operating credentials, including if those exact credentials
were reused by something other than this codebase.

The migration is guarded by `_is_postgresql(dialect_name)` and is a **no-op on
SQLite** — SQLite has no privilege/role system and does not support
`REVOKE`/`GRANT` syntax at all. Without this guard, `alembic upgrade head` would
fail outright for local development (ADR 0006/0012's SQLite path).

## Explicitly out of scope

- **No cryptographic tamper-evidence** (hash chaining, digital signatures). That
  is a materially larger design decision (key management, verification tooling,
  performance impact on every read) with no concrete requirement driving it yet
  in this repository — proposing it here would be speculative architecture.
  `REVOKE`-based enforcement addresses a different, narrower threat (accidental
  or routine mutation via the same credentials the app already has), not a
  fully adversarial one.
- **No enforcement mechanism for the in-memory store.** `InMemoryCustodyEventStore`
  has no privilege system to revoke anything from; its immutability remains
  code-convention-only, same as before. This is acceptable because the in-memory
  path is explicitly the dev/test fallback (ADR 0006), never the production
  persistence layer.

## Verification limitation (stated plainly)

This environment has no PostgreSQL instance available (no Docker/registry access
here — same constraint noted in ADR 0012). **The actual REVOKE/GRANT behavior
against real PostgreSQL has not been executed or verified in this session.**
What *is* verified, by an executed test
(`tests/unit/test_append_only_immutability_migration.py`), is:

- `_is_postgresql()`'s dialect-detection logic, directly.
- That `upgrade()`/`downgrade()` — the real migration functions, not a
  simulation — run against a live SQLite connection via Alembic's `Operations`
  context and correctly no-op without raising, so `alembic upgrade head`
  continues to work for local SQLite development after this migration is added.

Before relying on this in production, run `alembic upgrade head` against a real
PostgreSQL instance (the `postgres` service already in `docker-compose.yml`) and
confirm with `\dp custody_assertions` (or
`SELECT has_table_privilege(current_user, 'custody_assertions', 'UPDATE')`,
expecting `false`) that the revoke took effect, and that the application's normal
read/write flow (`INSERT`/`SELECT`, unaffected by this migration) still works.
