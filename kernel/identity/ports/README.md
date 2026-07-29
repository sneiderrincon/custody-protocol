# Identity Ports

Identity ports expose actor metadata needed by other contexts.

```mermaid
flowchart LR
  Custody[Custody Application] --> Registry[ActorRegistry]
  Registry --> Actor[Actor]
```

