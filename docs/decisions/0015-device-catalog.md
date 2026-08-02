# ADR 0015: Device Catalog Bounded Context

## Status

Accepted.

## Context

The platform connects Manufacturer, Distributor, and Hospital organizations, each
using different local product codes for the same physical medical device. Only
regulatory identifiers (UDI-DI, GMDN, manufacturer legal identity, INVIMA
registration) are globally trusted. The Custody Kernel (`kernel.custody`) correctly
stores immutable custody facts and must not be redesigned to carry product-name
semantics.

## Decision

**New bounded context, `kernel.catalog`, added inside the existing FastAPI app** (no
new deployable service — see "single app vs. microservices" below) with the exact
same layering as `kernel.custody`/`kernel.identity`: `domain` (Pydantic
`BaseModel`s, per ADR 0009), `ports` (`Protocol`), `application` (`DeviceCatalogService`),
`infrastructure` (in-memory + SQLAlchemy adapters). `CanonicalDevice` is the
aggregate root and the **only** place `generic_regulatory_name` and other
regulatory metadata are stored — never duplicated into a custody event.

**Single FastAPI app, not a new microservice.** There is no evidence in this
codebase of a scaling or team-boundary reason to split Catalog into its own
deployable service. Doing so now would be exactly the "unnecessary abstraction"
this project has consistently avoided (see ADR 0011's identical reasoning for
rate-limiting). `api/routes/catalog.py` is added as one more router in the existing
`create_app()`, sharing the existing JWT auth (ADR 0010), rate limiting
(ADR 0011), and CORS (ADR 0014) — all built once, reused, not reimplemented.

**Persistence: JSON columns for nested value objects, not normalized child
tables.** `regulatory_registrations`, `packaging`, `storage_conditions`,
`sterilization`, `manufacturer`, `gmdn` are stored as JSON on `catalog_devices`
(one migration, `0003_create_device_catalog`) rather than separate tables with
SQLAlchemy relationships. Nothing in this increment queries by, e.g., "devices
with an expiring registration" — normalizing prematurely for a query that doesn't
exist yet would be speculative. When that need is real, splitting
`regulatory_registrations` into its own table is a contained migration.

**Authorization: coarse-grained for now, explicitly not fine-grained yet.**
`POST /v1/catalog/devices` requires the same JWT authentication as custody writes
(any known, active actor) — it does **not** yet restrict registration to
Manufacturer-role organizations specifically, because `Organization`/`Role`/
`Permission` (the next increment, per the working plan) don't exist in code yet.
Inventing a `MANAGE_CATALOG` permission check against a role system that isn't
built would be exactly the kind of speculative code this project avoids. This is
tracked, not silently deferred: `register_device`'s docstring states this
explicitly, and the next increment (Organization) is expected to tighten this.

## Explicitly out of scope (this increment)

- `DeviceAlias` (Device Aliasing bounded context) — depends on `Organization`,
  which doesn't exist yet. Next increment.
- `Organization`, `Facility`, `Location`, `Role`, `Permission` — next increment.
- Any change to `kernel.custody` or `kernel.identity`'s existing code — none was
  needed or made.
- Event-sourcing the catalog. `CanonicalDevice` is versioned (optimistic
  concurrency), not append-only — it is master data whose current state is what
  matters operationally, unlike a physical custody fact. Adding an event log for
  catalog edits is a legitimate future idea but has no concrete requirement
  driving it in this increment.

## Consequences

- `kernel/README.md`'s dependency diagram now shows `api --> kernel.catalog`,
  keeping the documented diagram truthful (the same discipline ADR 0007 already
  established after finding an undocumented edge).
- Custody events remain semantically empty of product names, exactly as designed
  in the canonical semantic model document — `device_id` is the only link a
  custody event needs, and Catalog is where that ID resolves to meaning.
- `Base.metadata` (shared `kernel.shared.infrastructure.database.Base`) now
  includes `catalog_devices` alongside the existing custody tables — a single
  `alembic upgrade head` continues to provision the whole schema, no new
  migration entrypoint needed.
