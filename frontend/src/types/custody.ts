/**
 * Tipos derivados del contrato real de FastAPI.
 *
 * Fuente de verdad: el esquema OpenAPI que expone la app
 * (`GET /openapi.json`), no suposiciones de la UI. Los nombres de campo se
 * mantienen en snake_case a proposito: son exactamente los que viajan en el
 * JSON, asi cualquier divergencia con el backend falla en compilacion y no en
 * runtime frente a un cliente.
 */

/** Conjunto cerrado de eventos de custodia (`CustodyEventType`). */
export const CUSTODY_EVENT_TYPES = [
  "Fabricado",
  "Enviado",
  "Recibido",
  "Despachado",
  "UsadoImplantado",
  "Devuelto",
  "DadoDeBaja",
  "EstadoInicialDeclarado",
] as const;

export type CustodyEventType = (typeof CUSTODY_EVENT_TYPES)[number];

export interface EvidenceReference {
  uri: string;
  /** Digest SHA-256 en hexadecimal (64 caracteres). */
  sha256: string;
}

export interface PayloadAttribute {
  key: string;
  value: string | number | boolean | null;
}

export interface AssertionPayload {
  attributes: PayloadAttribute[];
}

export interface Provenance {
  /** UUID del actor. El backend no expone un nombre legible para el. */
  actor_id: string;
  adapter_id: string;
  declared_at: string;
  evidence: EvidenceReference[];
}

/** Aserción ya sellada en el registro append-only. */
export interface CommittedCustodyAssertion {
  claim_id: string;
  unit_id: string;
  event_type: CustodyEventType;
  occurred_at: string;
  provenance: Provenance;
  payload?: AssertionPayload;
  global_position: number;
  stream_version: number;
}

/**
 * Estado derivado de una unidad. Deliberadamente minimo: el backend no deriva
 * propietario, ubicacion ni estado comercial, y la UI no debe inventarlos.
 */
export interface CustodyStateProjection {
  unit_id: string;
  event_type: CustodyEventType | null;
  as_of_stream_version: number;
}

export interface HistoryResponse {
  assertions: CommittedCustodyAssertion[];
}

export interface StateResponse {
  state: CustodyStateProjection;
}

export interface AssertionResponse {
  assertion: CommittedCustodyAssertion;
}
