"""Rate limiting for write endpoints.

Fixed-window counter, in-memory, keyed by the authenticated actor (see
api/security.py, ADR 0010) rather than client IP — IP is unreliable behind
proxies/NAT and is no longer the strongest identity signal now that requests
are authenticated. See docs/decisions/0011-rate-limiting.md for the scope of
this decision: this is process-local by design because the current
deployment (docker-compose.yml) runs a single API replica with no shared
cache. Horizontal scaling requires a distributed backend, which is not built
here since nothing in this repo currently runs more than one replica.
"""

from __future__ import annotations

import os
from collections import defaultdict
from collections.abc import Callable
from functools import lru_cache
from threading import Lock
from time import monotonic
from uuid import UUID

from fastapi import Depends, HTTPException, status

from api.security import get_current_actor_id

DEFAULT_MAX_REQUESTS = 60
DEFAULT_WINDOW_SECONDS = 60.0


class RateLimiter:
    """Fixed-window request-rate limiter for a single logical endpoint group."""

    def __init__(
        self,
        *,
        max_requests: int,
        window_seconds: float,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        if max_requests < 1:
            msg = "max_requests must be at least 1"
            raise ValueError(msg)
        if window_seconds <= 0:
            msg = "window_seconds must be positive"
            raise ValueError(msg)
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._clock = clock
        self._lock = Lock()
        self._hits: dict[str, list[float]] = defaultdict(list)

    def check(self, key: str) -> None:
        """Raise HTTP 429 if `key` has exceeded the configured rate; else record a hit."""

        now = self._clock()
        window_start = now - self._window_seconds
        with self._lock:
            hits = [t for t in self._hits[key] if t > window_start]
            if len(hits) >= self._max_requests:
                self._hits[key] = hits
                retry_after = max(0, int(hits[0] + self._window_seconds - now) + 1)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="rate limit exceeded",
                    headers={"Retry-After": str(retry_after)},
                )
            hits.append(now)
            self._hits[key] = hits


@lru_cache
def get_write_rate_limiter() -> RateLimiter:
    """Build the write-endpoint limiter from environment configuration.

    Cached like api.dependencies.get_container: call
    ``get_write_rate_limiter.cache_clear()`` after changing the environment
    (production restarts the process instead; tests do this explicitly).
    """

    max_requests = int(os.getenv("RATE_LIMIT_WRITE_MAX_REQUESTS", str(DEFAULT_MAX_REQUESTS)))
    window_seconds = float(
        os.getenv("RATE_LIMIT_WRITE_WINDOW_SECONDS", str(DEFAULT_WINDOW_SECONDS))
    )
    return RateLimiter(max_requests=max_requests, window_seconds=window_seconds)


_ACTOR_DEPENDENCY = Depends(get_current_actor_id)


def enforce_write_rate_limit(actor_id: UUID = _ACTOR_DEPENDENCY) -> None:
    """FastAPI dependency: enforce the configured rate limit for write endpoints.

    Depends on the same authenticated actor_id as the route itself; FastAPI
    caches dependency resolution per request, so this does not re-verify the
    JWT a second time.
    """

    get_write_rate_limiter().check(str(actor_id))
