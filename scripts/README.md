# Scripts

Scripts automate generated artifacts that must remain reproducible.

```mermaid
flowchart LR
  App[FastAPI App] --> Export[scripts/export_openapi.py]
  Export --> OpenAPI[docs/openapi.json]
```

