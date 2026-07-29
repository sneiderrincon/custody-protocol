# ADR 0001: Adapter Boundary

## Status

Accepted for Iteration 1.

## Context

The requested repository structure includes `adapters/`, but the platform specification
states that production adapters must live in separate repositories from day one to protect
the Kernel from adapter volatility.

## Decision

Keep `adapters/` in this repository only as a contract and conformance boundary. Do not
place production SAP, Epic, or CSV adapter implementations here.

## Consequences

- The Kernel can expose stable grammar and tests for adapter authors.
- Production adapter repositories can evolve independently.
- The requested top-level structure remains visible without violating the specification's
  change-discipline requirement.

