import { useQuery } from "@tanstack/react-query";
import { fetchUnitHistory, fetchUnitState } from "../services/custodyService";

/** Historia completa de una unidad. Solo consulta cuando hay un `unitId`. */
export function useUnitHistory(unitId: string | null) {
  return useQuery({
    queryKey: ["custody", "history", unitId],
    queryFn: () => fetchUnitHistory(unitId!),
    enabled: Boolean(unitId),
    retry: false,
  });
}

/**
 * Estado derivado "a hoy". `asOf` se congela por consulta para que el
 * instante no cambie en cada re-render y react-query pueda cachear.
 */
export function useUnitState(unitId: string | null, asOf: string) {
  return useQuery({
    queryKey: ["custody", "state", unitId, asOf],
    queryFn: () => fetchUnitState(unitId!, new Date(asOf)),
    enabled: Boolean(unitId),
    retry: false,
  });
}
