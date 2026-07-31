from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi import HTTPException

from api.rate_limit import RateLimiter, enforce_write_rate_limit, get_write_rate_limiter

HTTP_TOO_MANY_REQUESTS = 429


class _FakeClock:
    """Deterministic, manually-advanced clock for testing time windows."""

    def __init__(self, start: float = 0.0) -> None:
        self._now = start

    def __call__(self) -> float:
        return self._now

    def advance(self, seconds: float) -> None:
        self._now += seconds


def test_allows_requests_up_to_the_limit() -> None:
    clock = _FakeClock()
    limiter = RateLimiter(max_requests=3, window_seconds=60, clock=clock)

    limiter.check("actor-a")
    limiter.check("actor-a")
    limiter.check("actor-a")  # exactly at the limit, should not raise


def test_blocks_the_request_that_exceeds_the_limit() -> None:
    clock = _FakeClock()
    limiter = RateLimiter(max_requests=2, window_seconds=60, clock=clock)
    limiter.check("actor-a")
    limiter.check("actor-a")

    with pytest.raises(HTTPException) as exc_info:
        limiter.check("actor-a")

    assert exc_info.value.status_code == HTTP_TOO_MANY_REQUESTS
    assert "Retry-After" in exc_info.value.headers


def test_keys_are_independent() -> None:
    clock = _FakeClock()
    limiter = RateLimiter(max_requests=1, window_seconds=60, clock=clock)
    limiter.check("actor-a")

    limiter.check("actor-b")  # different key, independent budget


def test_window_expiry_allows_requests_again() -> None:
    clock = _FakeClock()
    limiter = RateLimiter(max_requests=1, window_seconds=10, clock=clock)
    limiter.check("actor-a")

    with pytest.raises(HTTPException):
        limiter.check("actor-a")

    clock.advance(10.001)

    limiter.check("actor-a")  # window has elapsed, budget renewed


def test_rejects_non_positive_configuration() -> None:
    with pytest.raises(ValueError, match="max_requests"):
        RateLimiter(max_requests=0, window_seconds=60)
    with pytest.raises(ValueError, match="window_seconds"):
        RateLimiter(max_requests=1, window_seconds=0)


def test_get_write_rate_limiter_reads_environment_configuration(monkeypatch) -> None:
    expected_max_requests = 5
    expected_window_seconds = 30
    monkeypatch.setenv("RATE_LIMIT_WRITE_MAX_REQUESTS", str(expected_max_requests))
    monkeypatch.setenv("RATE_LIMIT_WRITE_WINDOW_SECONDS", str(expected_window_seconds))
    get_write_rate_limiter.cache_clear()

    try:
        limiter = get_write_rate_limiter()

        assert limiter._max_requests == expected_max_requests
        assert limiter._window_seconds == expected_window_seconds
    finally:
        get_write_rate_limiter.cache_clear()
        monkeypatch.delenv("RATE_LIMIT_WRITE_MAX_REQUESTS", raising=False)
        monkeypatch.delenv("RATE_LIMIT_WRITE_WINDOW_SECONDS", raising=False)


def test_enforce_write_rate_limit_uses_actor_id_as_key(monkeypatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_WRITE_MAX_REQUESTS", "1")
    monkeypatch.setenv("RATE_LIMIT_WRITE_WINDOW_SECONDS", "60")
    get_write_rate_limiter.cache_clear()
    actor_id = uuid4()

    try:
        enforce_write_rate_limit(actor_id)

        with pytest.raises(HTTPException) as exc_info:
            enforce_write_rate_limit(actor_id)
        assert exc_info.value.status_code == HTTP_TOO_MANY_REQUESTS

        # a different actor has an independent budget
        enforce_write_rate_limit(uuid4())
    finally:
        get_write_rate_limiter.cache_clear()
        monkeypatch.delenv("RATE_LIMIT_WRITE_MAX_REQUESTS", raising=False)
        monkeypatch.delenv("RATE_LIMIT_WRITE_WINDOW_SECONDS", raising=False)
