#!/usr/bin/env sh
# Docker entrypoint for the Kernel API.
#
# - Runs `alembic upgrade head` automatically when DATABASE_URL is set
#   (skipped for the in-memory dev/test configuration, ADR 0006).
# - `set -e` means a failing migration aborts the script with a non-zero
#   exit code *before* uvicorn ever starts, so the container fails fast and
#   is visibly unhealthy/exited rather than serving traffic against a
#   half-migrated schema.
# - `exec` replaces this shell with the uvicorn process (PID 1), so signals
#   (SIGTERM on `docker stop`) reach uvicorn directly for a clean shutdown.
set -eu

if [ -n "${DATABASE_URL:-}" ]; then
    echo "docker-entrypoint: DATABASE_URL is set, running alembic upgrade head..."
    alembic upgrade head
    echo "docker-entrypoint: migrations complete."
else
    echo "docker-entrypoint: DATABASE_URL is not set, skipping migrations (in-memory mode)."
fi

exec uvicorn api.main:app --host 0.0.0.0 --port 8000
