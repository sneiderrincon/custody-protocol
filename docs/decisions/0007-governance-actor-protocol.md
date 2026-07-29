# ADR 0007: Governance Depends on an Actor Protocol, Not on Identity's Domain

## Status

Accepted.

## Context

`kernel.governance.domain.policies.CustodyDeclarationPolicy` needs to know whether an
actor may declare custody claims. It previously imported `Actor` directly from
`kernel.identity.domain.actors`. That import was never declared in the kernel
dependency diagram (`kernel/README.md`), was not enforced by any architecture test,
and coupled the `governance` bounded context to `identity`'s concrete domain model —
a violation of bounded context isolation in DDD.

## Decision

`governance.domain.policies` defines its own local `AuthorizableActor` `Protocol`
describing only the two members the policy needs (`actor_id`, `can_declare_claims`).
`identity.domain.actors.Actor` already satisfies this shape structurally, so no other
module changes. `governance` no longer imports anything from `kernel.identity`.

## Consequences

- `governance`'s domain layer is self-contained: it only depends on its own types and
  on `kernel.custody.domain.assertions.CustodyAssertionDraft` (an existing, separate
  dependency, unchanged by this decision).
- Any future actor-like type from a different context (or a test double) can be
  authorized without importing `identity`, as long as it structurally matches
  `AuthorizableActor`.
- `tests/architecture/test_boundaries.py::test_governance_domain_does_not_import_identity`
  enforces this boundary going forward.
