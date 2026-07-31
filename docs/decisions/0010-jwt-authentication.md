# ADR 0010: JWT Bearer Authentication for the Custody Write Endpoint

## Status

Accepted.

## Context

`POST /v1/custody/assertions` accepted `provenance.actor_id` directly from the
request body. `ActorRegistry`/`CustodyDeclarationPolicy` (see ADR 0007) verify that
the named actor exists and is active, but nothing verified that the caller *was*
that actor — any client that knew or guessed a valid `actor_id` UUID could declare
custody assertions on that actor's behalf. Authorization without authentication is
not a meaningful trust boundary for a regulated custody log.

## Decision

- The write endpoint requires a JWT bearer token, verified server-side
  (`api/security.py::get_current_actor_id`, an `HS256`-signed token whose `sub`
  claim is the actor's UUID).
- `api/routes/custody.py::declare_assertion` **always overrides**
  `command.provenance.actor_id` with the authenticated actor_id from the token,
  regardless of what the request body contains. The body's `actor_id` field is
  kept in the schema for backward compatibility but is no longer authoritative.
- Authorization (is this actor allowed to declare claims) is unchanged and stays
  entirely in `kernel/custody/application` + `kernel/governance/domain` —
  authentication (who is this) is a new, separate concern that lives only in
  `api/`. `kernel/` does not import FastAPI or `jwt`; this is enforced by the
  existing `tests/architecture/test_boundaries.py::test_domain_does_not_import_infrastructure_or_api`.
- `fastapi.security.OAuth2PasswordBearer` is used as the auth scheme so the
  OpenAPI/Swagger UI presents the standard "Authorize" bearer-token flow.

## Explicitly out of scope

This ADR **verifies** tokens; it does not **issue** them. There is no
`/v1/auth/token` login endpoint, no password storage, and no credential-issuing
bounded context. `ActorRegistry` has no password field, and adding one — plus
hashing, a login flow, and token refresh — is a distinct, larger piece of work with
its own security surface. This kernel assumes tokens are issued by an external
identity provider that both parties trust, sharing `JWT_SECRET_KEY` for
verification (HS256). `OAuth2PasswordBearer(tokenUrl=...)` only needs a URL string
for documentation purposes; it does not require that URL to be implemented here.

A production identity provider integration (e.g. moving to RS256 + JWKS so the
Kernel never holds a shared secret) is a natural next step, but is speculative
without a chosen provider — not proposed here.

Read endpoints (`GET /units/{id}/history`, `GET /units/{id}/state`,
`GET /assertions/{claim_id}`) are **not** authenticated by this change. That is a
separate decision (should custody history be readable anonymously?) and is left
for a follow-up ADR rather than bundled into this fix.

## Consequences

- Any existing caller of `POST /v1/custody/assertions` without a bearer token now
  receives `401 Unauthorized`. This is an intentional, security-motivated breaking
  change to *unauthenticated* traffic — the entire purpose of this fix is that such
  traffic should no longer succeed. Request/response schemas are unchanged.
- `sdk/python/client.py::CustodyKernelClient.__init__` gained an optional
  `token: str | None = None` keyword parameter. Existing call sites compile and
  run unchanged; `declare_assertion` calls without a token will now receive a 401
  from the API, matching the API-side change.
- `JWT_SECRET_KEY` must be configured in every environment that runs the API
  (including `docker-compose.yml`), the same way `DATABASE_URL` already is
  (ADR 0006). Missing configuration fails closed (`RuntimeError`, not silent
  bypass), consistent with ADR 0002's fail-closed governance decision.
