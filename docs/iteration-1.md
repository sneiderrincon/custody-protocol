# Iteration 1: Kernel Design

## 1. Objetivo

Construir el primer Kernel de identidad y custodia como protocolo append-only. Esta
iteracion no implementa frontend, dashboards, IA, MLOps ni grafo dedicado.

## 2. Componentes afectados

- `kernel/custody`: dominio central, comandos, proyecciones, puerto de event store y store
  en memoria para pruebas.
- `kernel/shared`: errores compartidos.
- `adapters`: frontera de contratos y conformidad. Los adaptadores productivos viven en
  repositorios separados.
- `tests`: primeras pruebas unitarias, de integracion, property y arquitectura.

## 3. Bounded Contexts

- Identidad de Actores: actores institucionales, claves, incorporacion y confianza.
- Custodia: core domain tecnico. Afirmaciones de Custodia, invariantes, event store y
  estado derivado.
- Gobernanza y Consistencia: visibilidad cruzada, neutralidad, auditoria y reglas de acceso.
- Integracion: traduccion desde sistemas origen hacia la gramatica del dominio. En este
  repo solo existe como contrato/conformance.
- Conocimiento: proyecciones consultables derivadas. Sin reglas de negocio propias.
- Activacion: core domain comercial futuro que consume conocimiento y emite sus propios
  eventos, sin escribir directamente en Custodia.

## 4. Modelo DDD inicial

Entities:

- `CommittedCustodyAssertion`: afirmacion inmutable comprometida en el log.

Value Objects:

- `Provenance`: actor, adaptador, tiempo de declaracion y evidencia.
- `EvidenceReference`: URI y hash verificable de evidencia.
- `AssertionPayload`: metadatos opacos, inmutables y deterministas del adaptador.

Aggregates:

- `DeviceCustodyAggregate`: una unidad fisica rehidratada desde su stream completo.

Repositories:

- `CustodyEventStore`: puerto append-only para escribir y leer streams.

Factories:

- Pendiente de formalizar cuando existan varios origenes de comandos. Por ahora Pydantic
  valida drafts y comandos.

Policies:

- Precedencia temporal y de eventos en `VersionedCustodyRuleEngine`.
- Politicas de visibilidad cruzada quedan reservadas para Gobernanza en la siguiente
  iteracion de consistencia.

Domain Services:

- `VersionedCustodyRuleEngine`: reglas versionadas en codigo.
- `CustodyProjectionEngine`: reproduccion pura del log para derivar lecturas.

Application Services:

- `DeclareCustodyAssertionService`: unico caso de uso conceptual de escritura.

Commands:

- `DeclareCustodyAssertion`.

Domain Events:

- Custodia: `Fabricado`, `Enviado`, `Recibido`, `Despachado`, `UsadoImplantado`,
  `Devuelto`, `DadoDeBaja`, `EstadoInicialDeclarado`.

## 5. Riesgos

- La matriz de precedencia inicial es conservadora y debe contrastarse con datos reales de
  implementacion de referencia.
- El store en memoria no reemplaza PostgreSQL/EventStoreDB-like persistence; solo fija el
  contrato y las invariantes.
- Las reglas de visibilidad cruzada aun no estan implementadas; se reservaron para no
  inventar detalles fuera del material disponible.

## 6. Decisiones

- El repositorio contiene `adapters/` solo como frontera de contrato/conformance.
- Toda escritura entra como `DeclareCustodyAssertion`.
- El estado nunca se persiste como fuente de verdad; se deriva con replay.
- El motor de reglas es codigo versionado, no motor configurable generico.
- No se agrega snapshotting en esta iteracion.

## 7. Codigo

Archivos principales:

- `kernel/custody/domain/assertions.py`
- `kernel/custody/domain/events.py`
- `kernel/custody/domain/rules.py`
- `kernel/custody/domain/aggregate.py`
- `kernel/custody/ports/event_store.py`
- `kernel/custody/infrastructure/in_memory_event_store.py`
- `kernel/custody/application/services.py`
- `kernel/custody/application/projections.py`

## 8. Tests

- Unit tests: inmutabilidad, idempotencia, precedencia y estado derivado.
- Integration tests: contrato append-only, posiciones globales monotonicas y conflictos.
- Property tests: determinismo de proyecciones por replay.
- Architecture tests: separacion de dominio contra infraestructura/API y estructura base.
- Mutation tests: configurado `mutmut`; ejecucion queda para la siguiente iteracion cuando
  la suite base este aprobada.

## 9. Proximos pasos

1. Aprobar o ajustar la matriz de precedencia.
2. Implementar persistencia PostgreSQL con SQLAlchemy 2 y Alembic sin cambiar dominio.
3. Modelar y persistir `InconsistenciaRechazada` solo cuando exista su flujo append-only.
4. Definir suite de conformidad para adaptadores externos.
5. Introducir APIs FastAPI separando estrictamente escritura y lectura.
