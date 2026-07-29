# ADR 0006: SQLAlchemy PostgreSQL Adapter

## Status

Accepted.

## Context

The Kernel needs PostgreSQL persistence without leaking persistence details into the
domain.

## Decision

Implement SQLAlchemy adapters behind custody ports and define Alembic migrations for the
append-only logs.

## Consequences

- Domain code remains persistence-agnostic.
- PostgreSQL can enforce uniqueness for idempotency and stream monotonicity.
- Integration tests can still run against in-memory ports from the first commit.

