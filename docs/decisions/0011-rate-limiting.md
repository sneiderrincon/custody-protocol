# ADR 0011: In-Memory Fixed-Window Rate Limiting for Write Endpoints

## Status

Accepted.

## Context

`POST /v1/custody/assertions` had no request-rate protection. Once ADR 0010 added
authentication, a single valid but compromised (or malicious) actor credential could
still write to the custody log at unbounded speed — no per-actor throughput ceiling
existed.

## Decision

- `api/rate_limit.py::RateLimiter` implements a fixed-window counter, keyed per
  request key, thread-safe (`threading.Lock`), with an injectable clock for
  deterministic testing.
- `enforce_write_rate_limit` is a FastAPI dependency that keys the limiter by the
  **authenticated actor_id** (from ADR 0010's `get_current_actor_id`), not client
  IP: IP is unreliable behind proxies/NAT/shared egress, and actor identity is now
  a stronger, already-verified signal. FastAPI caches dependency resolution per
  request, so this does not re-verify the JWT a second time.
- Applied only to `POST /v1/custody/assertions` (the sole write endpoint), per the
  stated requirement — read endpoints are unaffected, matching ADR 0010's existing
  scope boundary (this ADR does not revisit that decision).
- Configurable via `RATE_LIMIT_WRITE_MAX_REQUESTS` (default 60) and
  `RATE_LIMIT_WRITE_WINDOW_SECONDS` (default 60), read the same way
  `DATABASE_URL`/`JWT_SECRET_KEY` are — environment variables, with the limiter
  built lazily and cached (`get_write_rate_limiter`, mirroring
  `api.dependencies.get_container`'s `@lru_cache` pattern already used in this
  codebase).
- Exceeding the limit returns `429 Too Many Requests` with a `Retry-After` header.

## Explicitly out of scope

This is a **process-local, in-memory** limiter by design. `docker-compose.yml`
defines exactly one `api` replica and no shared cache (no Redis, no Memcached) — a
distributed rate limiter would be infrastructure this repository has no evidence it
needs yet, and would be speculative architecture. If the API is later scaled to
multiple replicas, the limit becomes per-replica (an actor could get
`N × replica_count` requests through), which is a known, documented limitation, not
a silent gap. Migrating `RateLimiter`'s internal counter to a shared backend (e.g.
Redis) at that point does not require changing `enforce_write_rate_limit`'s public
signature — it is already isolated behind this one function.

## Consequences

- `POST /v1/custody/assertions` now returns `429` once an actor exceeds the
  configured rate within the window; previously unbounded traffic from a single
  actor is now capped by default (60 req/min).
- Restarting the API process resets all counters (in-memory, not persisted) — this
  is the same trade-off already accepted for `KernelContainer`'s in-memory fallback
  path (ADR 0006) and is consistent with this deployment's current architecture.
- `docker-compose.yml` gained two optional environment variables with safe
  defaults; omitting them does not break the deployment.
