import { apiClient } from "./apiClient";
import type { CanonicalDevice, DeviceResponse } from "../types/catalog";

/**
 * Acceso al catalogo canonico (`api/routes/catalog.py`).
 *
 * Limitacion del backend: no existe un endpoint de listado. Solo se puede
 * recuperar un dispositivo por `device_id` o por `udi_di` exacto, por eso la
 * UI es de busqueda y no de inventario.
 */

/** `GET /v1/catalog/devices/{device_id}` */
export async function fetchDeviceById(deviceId: string): Promise<CanonicalDevice> {
  const response = await apiClient.get<DeviceResponse>(
    `/v1/catalog/devices/${encodeURIComponent(deviceId)}`,
  );
  return response.device;
}

/** `GET /v1/catalog/devices?udi_di=` — coincidencia exacta, no busqueda parcial. */
export async function fetchDeviceByUdiDi(udiDi: string): Promise<CanonicalDevice> {
  const query = new URLSearchParams({ udi_di: udiDi });
  const response = await apiClient.get<DeviceResponse>(`/v1/catalog/devices?${query}`);
  return response.device;
}

/** `POST /v1/catalog/devices` — requiere JWT. */
export async function registerDevice(command: unknown): Promise<CanonicalDevice> {
  const response = await apiClient.post<DeviceResponse>("/v1/catalog/devices", command);
  return response.device;
}
