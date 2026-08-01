# ADR 0014: Configurable, Fail-Closed CORS

## Status

Accepted.

## Context

The API had no `CORSMiddleware`, so no browser-based client (e.g. a local HTML
console, `docker-entrypoint.sh`'s neighbor `custody_kernel_console.html`) could
call it directly — browsers block cross-origin `fetch()` responses without the
right CORS headers, regardless of whether the request itself would have
succeeded.

## Decision

`api/main.py::create_app()` reads `CORS_ALLOWED_ORIGINS` (comma-separated) and
only registers `CORSMiddleware` when at least one origin is configured — this
follows the same fail-closed pattern already used for `JWT_SECRET_KEY`
(ADR 0010) and `ActorRegistry` (ADR 0002): unset means nothing is allowed, not
"allow everything". `allow_credentials=True` with `allow_methods` restricted to
`GET`/`POST` and `allow_headers` restricted to `Authorization`/`Content-Type`
(the only ones this API's endpoints need).

## Explicitly out of scope

- No wildcard (`*`) origin by default in `docker-compose.yml` — that is a
  deliberate choice left to whoever deploys this, not a default this repo
  ships with. Local development against the console
  (`custody_kernel_console.html`) requires explicitly setting
  `CORS_ALLOWED_ORIGINS` to the console's actual origin.
- No per-route CORS configuration — this API has one logical client surface
  (the console/any browser-based tool), so a single origin list is sufficient;
  splitting it per-route would be speculative given nothing in this repo needs
  different origins for different endpoints.

## Consequences

- Deploying with `CORS_ALLOWED_ORIGINS` unset (the default) behaves exactly as
  before this change — no browser can call the API cross-origin, same as
  today's `main` branch.
- A local console opened as a `file://` document sends `Origin: null`, which
  most browsers do **not** match against an explicit origin string. The
  practical way to use `custody_kernel_console.html` locally is to serve it
  over `http://` (e.g. `python -m http.server`) from a fixed port and set
  `CORS_ALLOWED_ORIGINS` to that exact origin.
