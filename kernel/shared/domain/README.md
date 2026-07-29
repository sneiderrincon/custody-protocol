# Shared Domain

Shared domain contains base exceptions and primitives used by multiple contexts.

```mermaid
classDiagram
  class DomainError
  class ConcurrencyConflictError
  class IdempotencyConflictError
  DomainError <|-- ConcurrencyConflictError
  DomainError <|-- IdempotencyConflictError
```

