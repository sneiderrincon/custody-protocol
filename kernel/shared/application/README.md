# Shared Application

Reserved for cross-cutting application abstractions.

```mermaid
flowchart LR
  ServiceA[Application Service] --> Shared[Shared Application Primitive]
  Shared --> ServiceB[Application Service]
```

