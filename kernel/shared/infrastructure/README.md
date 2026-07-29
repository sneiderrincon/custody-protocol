# Shared Infrastructure

Shared infrastructure contains reusable technical adapters such as database wiring.

```mermaid
flowchart LR
  Infra[Context Infrastructure] --> Database[Database Helpers]
  Database --> SQLAlchemy[SQLAlchemy]
```

