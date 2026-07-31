# ADR 0012: Production Bootstrap — Automatic Migrations, Healthcheck, Fail-Fast Startup

## Status

Accepted.

## Context

`Dockerfile`'s `CMD` only ran `uvicorn`. Nothing ran `alembic upgrade head`. On a
fresh `docker compose up` with an empty `postgres-data` volume, the API container
started successfully and appeared healthy, but every request failed with
`relation "custody_assertions" does not exist` — the container looked up but was
not actually usable. Separately, misconfiguration (missing `JWT_SECRET_KEY`, an
unreachable database) only surfaced as a 500 on the first real request, not as a
startup failure — much harder to diagnose in an orchestrator that only checks
"is the process running."

## Decision

- **`docker-entrypoint.sh`** (new) runs `alembic upgrade head` automatically when
  `DATABASE_URL` is set, then `exec`s into `uvicorn`. `set -eu` means a failing
  migration aborts the container with a non-zero exit code *before* uvicorn ever
  binds a port — the container fails fast and shows as `Exited`, not `Up`
  serving broken requests. Migrations are skipped (not attempted) when
  `DATABASE_URL` is unset, matching the existing in-memory dev/test path
  (ADR 0006) — there is nothing to migrate.
- **`Dockerfile`** installs the entrypoint script as `ENTRYPOINT`, and adds a
  native `HEALTHCHECK` using `python -c "import urllib.request..."` (the
  `python:3.13-slim` base has no `curl`; this avoids adding an OS package for a
  single check).
- **`api/routes/health.py`** (new) — `GET /healthz`, deliberately unauthenticated
  (health checks are an operational concern, not custody data, consistent with
  ADR 0010's scope). Calls `KernelContainer.ping()`.
- **`KernelContainer.ping()`** (new method, `api/dependencies.py`) — executes
  `SELECT 1` against the tracked session when DB-backed; no-op for the in-memory
  path. Deliberately not implemented via `event_store.all()`, which would
  reintroduce the full-log-scan pattern already flagged as a separate,
  unrelated finding.
- **`api/main.py`** gained a `lifespan` context manager that calls
  `_validate_startup_configuration()` once, at process start: fails immediately
  if `JWT_SECRET_KEY` is missing, and calls `ping()` to confirm DB reachability
  when configured. This is verified to actually run — Starlette's `TestClient`
  only triggers lifespan events when used as a context manager
  (`with TestClient(app):`), which is why the affected tests use that form
  explicitly (see `tests/integration/test_startup_and_health.py`), unlike the
  existing tests elsewhere in this suite which construct `TestClient(app)`
  directly.

## Explicitly out of scope

- No separate migration job/init-container. `docker-compose.yml` runs exactly one
  `api` replica; running migrations inline in the entrypoint is safe at that
  scale. If this is later scaled to multiple replicas starting concurrently,
  migrations should move to a dedicated one-shot step to avoid concurrent
  `alembic upgrade` races — not built here since nothing in this repo runs more
  than one replica today (same reasoning already applied to rate limiting,
  ADR 0011).
- `/healthz` does not distinguish liveness from readiness (Kubernetes-style two
  separate probes) — this repo has one health signal today; splitting it is
  speculative without an orchestrator that would use the distinction.

## Consequences

- `docker compose up` against a fresh volume now actually works end-to-end:
  migrations run, then the API starts, instead of starting broken.
- A misconfigured deployment (missing secret, bad `DATABASE_URL`) now exits
  immediately with a clear log line, instead of accepting traffic and failing
  requests one at a time.
- `docker build`/`docker compose up` itself was not run in this environment (no
  Docker daemon / registry access here) — `docker-entrypoint.sh` was verified
  with `sh -n` (syntax) and the Python code paths it depends on
  (`KernelContainer.ping`, `_validate_startup_configuration`, `/healthz`) are
  covered by `tests/integration/test_startup_and_health.py`. A real
  `docker compose up` run is recommended before relying on this in production.
