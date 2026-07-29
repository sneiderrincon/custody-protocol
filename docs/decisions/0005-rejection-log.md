# ADR 0005: Rejection Log

## Status

Accepted.

## Context

Rejected attempts are operationally important but are not custody assertions because they
do not claim a physical fact.

## Decision

Persist rejected attempts in a separate append-only `RejectionLog`.

## Consequences

- The custody event store remains pure.
- Adapter health can be observed through rejection events.
- Rejections can be audited without treating them as device lifecycle facts.

