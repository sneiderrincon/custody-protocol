# Adapter Contract Boundary

Production adapters are external to this repository.

An adapter may connect to the Kernel only after proving that it emits valid
`DeclareCustodyAssertion` commands:

- event type belongs to the closed custody vocabulary;
- provenance identifies actor, adapter and evidence;
- timestamps are timezone-aware;
- assertions satisfy custody precedence rules;
- repeated delivery uses the same `claim_id` and identical content;
- no adapter writes directly to projections or state tables.

