# Python SDK

The Python SDK submits validated custody commands to the HTTP API.

```mermaid
flowchart LR
  PythonApp[Python App] --> Client[CustodyKernelClient]
  Client --> API[HTTP API]
```

