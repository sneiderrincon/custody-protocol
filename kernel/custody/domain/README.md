# Custody Domain

The custody domain contains only physical-device custody language and invariants.

```mermaid
classDiagram
  class CustodyAssertionDraft
  class CommittedCustodyAssertion
  class DeviceCustodyAggregate
  class VersionedCustodyRuleEngine
  CustodyAssertionDraft <|-- CommittedCustodyAssertion
  DeviceCustodyAggregate --> CommittedCustodyAssertion
  VersionedCustodyRuleEngine --> CustodyAssertionDraft
```

