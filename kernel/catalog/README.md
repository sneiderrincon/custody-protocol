# Catalog Package

Device Catalog is the canonical regulatory identity of medical devices -- master
data, not a custody fact. It never references a physical unit's current custody
state; Custody references it by `device_id`, not the other way around.

```mermaid
flowchart LR
  Command[RegisterCanonicalDevice] --> Service[DeviceCatalogService]
  Service --> Repository[DeviceCatalogRepository Port]
  Repository --> Store[(Canonical Devices)]
```
