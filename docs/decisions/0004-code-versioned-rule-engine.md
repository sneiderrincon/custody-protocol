# ADR 0004: Code-Versioned Rule Engine

## Status

Accepted.

## Context

The specification rejects a configurable general-purpose rule engine in the current phase.

## Decision

Implement custody consistency as code-versioned domain logic in
`VersionedCustodyRuleEngine`.

## Consequences

- Rule changes are reviewed as Kernel code changes.
- The system avoids premature customer-specific configurability.
- Future jurisdictional variation requires evidence before adding a configurable engine.

