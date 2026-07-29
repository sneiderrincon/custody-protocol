# ADR 0003: CQRS Boundary

## Status

Accepted.

## Context

The write API must remain small and stable while read APIs may evolve through derived
projections.

## Decision

Expose a single conceptual write route for declaring custody assertions. Read routes use
projection engines over the event log and never write.

## Consequences

- Write integrity is protected by a small command surface.
- Read models can evolve without becoming sources of truth.
- API routing must preserve command/query separation.

