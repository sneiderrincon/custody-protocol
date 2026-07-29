# Identity Package

Identity models institutional actors and their trust metadata.

```mermaid
flowchart LR
  Registry[ActorRegistry Port] --> Actor[Actor]
  Actor --> Status[ActorStatus]
  Actor --> Trust[TrustLevel]
```

