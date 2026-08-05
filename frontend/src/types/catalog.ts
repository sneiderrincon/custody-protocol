/**
 * Tipos del catalogo canonico, derivados del esquema OpenAPI real de FastAPI
 * (`CanonicalDevice` y sus value objects). Ver nota en `types/custody.ts`
 * sobre por que se conserva snake_case.
 */

export const ISSUING_AGENCIES = ["GS1", "HIBCC", "ICCBBA"] as const;
export type IssuingAgency = (typeof ISSUING_AGENCIES)[number];

export const RISK_CLASSES = ["I", "IIa", "IIb", "III"] as const;
export type RiskClass = (typeof RISK_CLASSES)[number];

export const CATALOG_STATUSES = ["draft", "active", "discontinued", "recalled"] as const;
export type CatalogStatus = (typeof CATALOG_STATUSES)[number];

export const REGISTRATION_STATUSES = ["active", "expired", "suspended"] as const;
export type RegistrationStatus = (typeof REGISTRATION_STATUSES)[number];

export interface UdiDi {
  value: string;
  issuing_agency: IssuingAgency;
}

export interface ManufacturerIdentity {
  legal_name: string;
  invima_manufacturer_id?: string | null;
}

export interface GmdnCode {
  code: string;
  term: string;
}

export interface PackagingLevel {
  unit: string;
  quantity: number;
}

export interface PackagingSpec {
  /** El backend exige al menos un nivel. */
  levels: PackagingLevel[];
}

export interface StorageCondition {
  temperature_min_celsius?: number | null;
  temperature_max_celsius?: number | null;
  humidity_max_percent?: number | null;
  light_sensitive: boolean;
}

export interface SterilizationCondition {
  is_sterile: boolean;
  method?: string | null;
}

export interface RegulatoryRegistration {
  registration_id: string;
  /** Codigo ISO de dos letras. */
  country: string;
  authority: string;
  registration_number: string;
  valid_from: string;
  valid_until?: string | null;
  status: RegistrationStatus;
}

/** Identidad regulatoria unica de un modelo de dispositivo medico. */
export interface CanonicalDevice {
  device_id: string;
  udi_di: UdiDi;
  generic_regulatory_name: string;
  manufacturer: ManufacturerIdentity;
  manufacturer_model_reference: string;
  gmdn: GmdnCode;
  risk_class: RiskClass;
  regulatory_registrations: RegulatoryRegistration[];
  packaging: PackagingSpec;
  unit_of_measure: string;
  minimum_consumption_unit: string;
  storage_conditions: StorageCondition;
  sterilization: SterilizationCondition;
  commercial_presentation: string;
  lifecycle_status: CatalogStatus;
  version: number;
}

export interface DeviceResponse {
  device: CanonicalDevice;
}
