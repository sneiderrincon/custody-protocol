import { useMemo, useState, type FormEvent } from "react";
import { useSearchParams } from "react-router-dom";
import { Layers3, Search, ShieldCheck } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Badge } from "../components/ui/badge";
import { AssertionTimeline } from "../components/custody/AssertionTimeline";
import { EmptyState, ErrorState, LoadingState } from "../components/QueryState";
import { useUnitHistory, useUnitState } from "../hooks/useCustody";
import { eventLabel, eventTone } from "../lib/custodyLabels";

/**
 * Pantalla de trazabilidad: busqueda por `unit_id` y cadena de custodia.
 *
 * Es busqueda-primero y no inventario porque el backend no expone ningun
 * endpoint de listado -- solo consulta puntual por identificador.
 */
export function TrazabilidadPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const unitId = searchParams.get("unidad");

  const [draft, setDraft] = useState(unitId ?? "");

  // Instante fijo por unidad consultada: evita que `at` cambie en cada render.
  const asOf = useMemo(() => new Date().toISOString(), [unitId]);

  const history = useUnitHistory(unitId);
  const state = useUnitState(unitId, asOf);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = draft.trim();
    setSearchParams(trimmed ? { unidad: trimmed } : {}, { replace: false });
  }

  return (
    <div className="mt-6 space-y-6">
      <Card>
        <CardContent>
          <form className="flex flex-col gap-4 sm:flex-row sm:items-end" onSubmit={handleSubmit}>
            <div className="flex-1 space-y-2">
              <Label htmlFor="unidad">Identificador de unidad</Label>
              <Input
                id="unidad"
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                placeholder="udi_di:00812345678901/serial:MX-2048-1190"
                className="font-mono"
                autoComplete="off"
              />
            </div>
            <Button type="submit" variant="primary" className="sm:w-auto">
              <Search className="h-4 w-4" />
              Consultar cadena
            </Button>
          </form>
          <p className="mt-3 text-xs text-muted">
            La búsqueda es por coincidencia exacta del identificador de unidad.
          </p>
        </CardContent>
      </Card>

      {!unitId && (
        <EmptyState
          title="Consulta una unidad para empezar"
          copy="Introduce el identificador de una unidad física para reconstruir su cadena de custodia completa, evento por evento, con la evidencia asociada a cada declaración."
        />
      )}

      {unitId && history.isPending && <LoadingState />}

      {unitId && history.isError && <ErrorState error={history.error} />}

      {unitId && history.isSuccess && history.data.length === 0 && (
        <EmptyState
          title="Sin aserciones para esta unidad"
          copy="El identificador es válido, pero todavía no existe ninguna declaración de custodia registrada para esta unidad."
        />
      )}

      {unitId && history.isSuccess && history.data.length > 0 && (
        <>
          <div className="grid gap-3 sm:grid-cols-3">
            <SummaryCard
              icon={ShieldCheck}
              label="Estado derivado"
              value={
                state.isSuccess && state.data.event_type ? (
                  <Badge tone={eventTone(state.data.event_type)}>
                    {eventLabel(state.data.event_type)}
                  </Badge>
                ) : state.isPending ? (
                  <span className="text-sm text-muted">calculando…</span>
                ) : (
                  <span className="text-sm text-muted">sin estado</span>
                )
              }
            />
            <SummaryCard
              icon={Layers3}
              label="Versión del stream"
              value={
                <span className="font-mono text-lg">
                  {state.isSuccess ? state.data.as_of_stream_version : "—"}
                </span>
              }
            />
            <SummaryCard
              icon={Layers3}
              label="Aserciones registradas"
              value={<span className="font-mono text-lg">{history.data.length}</span>}
            />
          </div>

          <AssertionTimeline assertions={history.data} />
        </>
      )}
    </div>
  );
}

function SummaryCard({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Search;
  label: string;
  value: React.ReactNode;
}) {
  return (
    <Card className="p-4">
      <div className="grid h-9 w-9 place-items-center rounded-md border border-border bg-[#111418] text-accent">
        <Icon className="h-4 w-4" />
      </div>
      <div className="mt-4 font-mono text-[10px] uppercase tracking-[0.08em] text-[#66707B]">
        {label}
      </div>
      <div className="mt-2">{value}</div>
    </Card>
  );
}
