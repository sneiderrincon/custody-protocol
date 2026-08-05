import { useState, type FormEvent, type ReactNode } from "react";
import { useSearchParams } from "react-router-dom";
import {
  Boxes,
  Building2,
  Search,
  Snowflake,
  Stamp,
  Tags,
  Thermometer,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Card, CardContent, CardHeader } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { EmptyState, ErrorState, LoadingState } from "../components/QueryState";
import { useDeviceByUdiDi } from "../hooks/useCatalog";
import { ApiError } from "../services/apiClient";
import type { CanonicalDevice, StorageCondition } from "../types/catalog";

const LIFECYCLE_TONES = {
  draft: "default",
  active: "success",
  discontinued: "default",
  recalled: "danger",
} as const;

const REGISTRATION_TONES = {
  active: "success",
  expired: "default",
  suspended: "danger",
} as const;

/** Consulta del catalogo canonico por UDI-DI (coincidencia exacta). */
export function CatalogoPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const udiDi = searchParams.get("udi");

  const [draft, setDraft] = useState(udiDi ?? "");
  const device = useDeviceByUdiDi(udiDi);

  const notFound = device.error instanceof ApiError && device.error.isNotFound;

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = draft.trim();
    setSearchParams(trimmed ? { udi: trimmed } : {});
  }

  return (
    <div className="mt-6 space-y-6">
      <Card>
        <CardContent>
          <form className="flex flex-col gap-4 sm:flex-row sm:items-end" onSubmit={handleSubmit}>
            <div className="flex-1 space-y-2">
              <Label htmlFor="udi">UDI-DI</Label>
              <Input
                id="udi"
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                placeholder="00812345678901"
                className="font-mono"
                autoComplete="off"
              />
            </div>
            <Button type="submit" variant="primary" className="sm:w-auto">
              <Search className="h-4 w-4" />
              Buscar dispositivo
            </Button>
          </form>
        </CardContent>
      </Card>

      {!udiDi && (
        <EmptyState
          title="Consulta la identidad regulatoria de un dispositivo"
          copy="Introduce un UDI-DI para ver el registro canónico: fabricante legal, clasificación GMDN, clase de riesgo, registros sanitarios, empaque y condiciones de conservación."
        />
      )}

      {udiDi && device.isPending && <LoadingState label="Consultando el catálogo" />}

      {udiDi && notFound && (
        <EmptyState
          title="Sin registro en el catálogo"
          copy={`No existe ninguna entrada canónica para el UDI-DI ${udiDi}.`}
        />
      )}

      {udiDi && device.isError && !notFound && <ErrorState error={device.error} />}

      {udiDi && device.isSuccess && <DeviceRecord device={device.data} />}
    </div>
  );
}

function DeviceRecord({ device }: { device: CanonicalDevice }) {
  return (
    <div className="space-y-5">
      <Card>
        <CardContent className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone={LIFECYCLE_TONES[device.lifecycle_status]}>
                {device.lifecycle_status}
              </Badge>
              <Badge tone="accent">Clase {device.risk_class}</Badge>
              <Badge className="font-mono">v{device.version}</Badge>
            </div>
            <h2 className="mt-3 text-xl font-semibold">{device.generic_regulatory_name}</h2>
            <p className="mt-1 text-sm text-muted">{device.commercial_presentation}</p>
          </div>

          <div className="shrink-0 rounded-lg border border-border bg-[#111418] px-4 py-3">
            <div className="font-mono text-[10px] uppercase tracking-[0.08em] text-[#66707B]">
              UDI-DI · {device.udi_di.issuing_agency}
            </div>
            <div className="mt-1 break-all font-mono text-sm">{device.udi_di.value}</div>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-5 lg:grid-cols-2">
        <Section icon={Building2} title="Fabricante legal">
          <Field label="Razón social" value={device.manufacturer.legal_name} />
          <Field
            label="ID INVIMA"
            value={device.manufacturer.invima_manufacturer_id ?? "no registrado"}
            mono
          />
          <Field label="Referencia del modelo" value={device.manufacturer_model_reference} mono />
        </Section>

        <Section icon={Tags} title="Clasificación">
          <Field label="GMDN" value={`${device.gmdn.code} — ${device.gmdn.term}`} />
          <Field label="Clase de riesgo" value={device.risk_class} />
          <Field label="Unidad de medida" value={device.unit_of_measure} />
          <Field label="Unidad mínima de consumo" value={device.minimum_consumption_unit} />
        </Section>

        <Section icon={Boxes} title="Empaque">
          {device.packaging.levels.map((level, index) => (
            <Field
              key={`${level.unit}-${index}`}
              label={`Nivel ${index + 1}`}
              value={`${level.unit} × ${level.quantity}`}
            />
          ))}
        </Section>

        <Section icon={Thermometer} title="Conservación">
          <Field label="Temperatura" value={temperatureRange(device.storage_conditions)} />
          <Field
            label="Humedad máxima"
            value={
              device.storage_conditions.humidity_max_percent === null ||
              device.storage_conditions.humidity_max_percent === undefined
                ? "sin restricción"
                : `${device.storage_conditions.humidity_max_percent} %`
            }
          />
          <Field
            label="Fotosensible"
            value={device.storage_conditions.light_sensitive ? "sí" : "no"}
          />
        </Section>

        <Section icon={Snowflake} title="Esterilización">
          <Field label="Estéril" value={device.sterilization.is_sterile ? "sí" : "no"} />
          <Field label="Método" value={device.sterilization.method ?? "no aplica"} />
        </Section>

        <Section icon={Stamp} title="Registros sanitarios">
          {device.regulatory_registrations.length === 0 ? (
            <p className="text-sm text-muted">Sin registros sanitarios asociados.</p>
          ) : (
            <ul className="space-y-3">
              {device.regulatory_registrations.map((registration) => (
                <li
                  key={registration.registration_id}
                  className="rounded-md border border-border bg-[#111418] p-3"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="text-sm font-semibold">
                      {registration.authority} · {registration.country}
                    </span>
                    <Badge tone={REGISTRATION_TONES[registration.status]}>
                      {registration.status}
                    </Badge>
                  </div>
                  <div className="mt-1 font-mono text-xs text-muted">
                    {registration.registration_number}
                  </div>
                  <div className="mt-1 font-mono text-[11px] text-[#66707B]">
                    {registration.valid_from} → {registration.valid_until ?? "sin vencimiento"}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Section>
      </div>
    </div>
  );
}

function temperatureRange(storage: StorageCondition): string {
  const { temperature_min_celsius: min, temperature_max_celsius: max } = storage;

  if (min === null || min === undefined) {
    if (max === null || max === undefined) return "sin restricción";
    return `hasta ${max} °C`;
  }
  if (max === null || max === undefined) return `desde ${min} °C`;
  return `${min} °C a ${max} °C`;
}

function Section({
  icon: Icon,
  title,
  children,
}: {
  icon: typeof Boxes;
  title: string;
  children: ReactNode;
}) {
  return (
    <Card>
      <CardHeader className="flex items-center gap-3">
        <div className="grid h-8 w-8 place-items-center rounded-md border border-border bg-[#111418] text-accent">
          <Icon className="h-4 w-4" />
        </div>
        <h3 className="font-semibold">{title}</h3>
      </CardHeader>
      <CardContent className="space-y-3">{children}</CardContent>
    </Card>
  );
}

function Field({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
      <dt className="font-mono text-[10px] uppercase tracking-[0.08em] text-[#66707B]">
        {label}
      </dt>
      <dd className={`min-w-0 text-right text-sm ${mono ? "break-all font-mono text-xs" : ""}`}>
        {value}
      </dd>
    </div>
  );
}
