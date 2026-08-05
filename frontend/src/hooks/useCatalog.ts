import { useQuery } from "@tanstack/react-query";
import { fetchDeviceByUdiDi } from "../services/catalogService";

/**
 * Busqueda de dispositivo por UDI-DI. El backend solo soporta coincidencia
 * exacta -- no hay busqueda parcial ni listado.
 */
export function useDeviceByUdiDi(udiDi: string | null) {
  return useQuery({
    queryKey: ["catalog", "device", "udi-di", udiDi],
    queryFn: () => fetchDeviceByUdiDi(udiDi!),
    enabled: Boolean(udiDi),
    retry: false,
  });
}
