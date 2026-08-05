import { apiClient } from "./apiClient";
import type {
  AssertionResponse,
  CommittedCustodyAssertion,
  CustodyStateProjection,
  HistoryResponse,
  StateResponse,
} from "../types/custody";

/**
 * Acceso a los endpoints reales de custodia. Cada funcion corresponde 1:1 con
 * una ruta que existe hoy en `api/routes/custody.py`; no hay ninguna otra.
 */

/** `GET /v1/custody/units/{unit_id}/history` */
export async function fetchUnitHistory(
  unitId: string,
): Promise<CommittedCustodyAssertion[]> {
  const response = await apiClient.get<HistoryResponse>(
    `/v1/custody/units/${encodeURIComponent(unitId)}/history`,
  );
  return response.assertions;
}

/**
 * `GET /v1/custody/units/{unit_id}/state`
 *
 * El backend exige el instante de consulta (`at`): el estado es siempre
 * "a una fecha", nunca un presente implicito.
 */
export async function fetchUnitState(
  unitId: string,
  at: Date = new Date(),
): Promise<CustodyStateProjection> {
  const query = new URLSearchParams({ at: at.toISOString() });
  const response = await apiClient.get<StateResponse>(
    `/v1/custody/units/${encodeURIComponent(unitId)}/state?${query}`,
  );
  return response.state;
}

/** `GET /v1/custody/assertions/{claim_id}` */
export async function fetchAssertion(claimId: string): Promise<CommittedCustodyAssertion> {
  const response = await apiClient.get<AssertionResponse>(
    `/v1/custody/assertions/${encodeURIComponent(claimId)}`,
  );
  return response.assertion;
}

/**
 * `POST /v1/custody/assertions`
 *
 * El `actor_id` que se envie en `provenance` es irrelevante: el backend lo
 * sobrescribe con el actor del JWT verificado (api/routes/custody.py:71).
 */
export async function declareAssertion(
  command: unknown,
): Promise<CommittedCustodyAssertion> {
  const response = await apiClient.post<AssertionResponse>("/v1/custody/assertions", command);
  return response.assertion;
}
