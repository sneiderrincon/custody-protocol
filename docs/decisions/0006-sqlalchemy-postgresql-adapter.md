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

## Amendment (composition root wiring)

`api/dependencies.py::KernelContainer` now reads `DATABASE_URL` at startup. When set
(as `docker-compose.yml` already declared), the API wires
`SqlAlchemyCustodyEventStore`/`SqlAlchemyRejectionLog` instead of the in-memory ports,
committing the bound session after each append so assertions are durable across
requests and restarts. When `DATABASE_URL` is unset, the API keeps using the in-memory
ports, unchanged, for local development and tests. Schema creation is still owned by
Alembic (`alembic upgrade head`), not by the composition root.

