import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../services/apiClient";

/**
 * Estado real del backend contra `GET /healthz`. Sustituye a los indicadores
 * de disponibilidad que antes estaban cableados en la UI.
 */
export function useHealth() {
  return useQuery({
    queryKey: ["healthz"],
    queryFn: () => apiClient.get<unknown>("/healthz"),
    refetchInterval: 30_000,
    retry: false,
    staleTime: 15_000,
  });
}
