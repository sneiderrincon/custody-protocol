import { useQuery } from "@tanstack/react-query";
import { fetchDeviceCustody } from "../services/custodyService";

export function useDeviceCustody(unitId: string) {
  return useQuery({
    queryKey: ["device-custody", unitId],
    queryFn: () => fetchDeviceCustody(unitId),
  });
}
