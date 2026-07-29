"""Shared domain exceptions."""


class DomainError(Exception):
    """Base class for domain-level invariant violations."""


class ConcurrencyConflictError(DomainError):
    """Raised when an append would break stream version expectations."""


class IdempotencyConflictError(DomainError):
    """Raised when the same idempotency key is reused for different content."""
