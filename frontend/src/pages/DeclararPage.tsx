import { useState } from "react";
import { useForm } from "react-hook-form";
import { useMutation } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { AlertTriangle, CheckCircle2, DatabaseZap, Loader2 } from "lucide-react";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Card, CardContent, CardHeader } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Select } from "../components/ui/select";
import { useSession } from "../auth/SessionContext";
import { declareAssertion } from "../services/custodyService";
import { canWrite } from "../services/apiClient";
import { eventLabel, formatInstant } from "../lib/custodyLabels";
import { CUSTODY_EVENT_TYPES, type CommittedCustodyAssertion } from "../types/custody";

interface DeclareForm {
  unit_id: string;
  event_type: string;
  occurred_at: string;
  adapter_id: string;
  evidence_uri: string;
  evidence_sha256: string;
}

/** Valor para <input type="datetime-local"> en hora local del navegador. */
function nowForInput(): string {
  const now = new Date();
  const offsetMs = now.getTimezoneOffset() * 60_000;
  return new Date(now.getTime() - offsetMs).toISOString().slice(0, 16);
}

export function DeclararPage() {
  const { session } = useSession();
  const [committed, setCommitted] = useState<CommittedCustodyAssertion | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<DeclareForm>({
    defaultValues: {
      unit_id: "",
      event_type: CUSTODY_EVENT_TYPES[0],
      occurred_at: nowForInput(),
      adapter_id: "consola-web",
      evidence_uri: "",
      evidence_sha256: "",
    },
  });

  const mutation = useMutation({
    mutationFn: (form: DeclareForm) => {
      const occurredAt = new Date(form.occurred_at).toISOString();
      const hasEvidence = form.evidence_uri.trim() && form.evidence_sha256.trim();

      return declareAssertion({
        claim_id: crypto.randomUUID(),
        unit_id: form.unit_id.trim(),
        event_type: form.event_type,
        occurred_at: occurredAt,
        provenance: {
          // El backend descarta este valor y usa el actor del JWT verificado.
          actor_id: session?.actorId,
          adapter_id: form.adapter_id.trim(),
          declared_at: new Date().toISOString(),
          evidence: hasEvidence
            ? [{ uri: form.evidence_uri.trim(), sha256: form.evidence_sha256.trim() }]
            : [],
        },
      });
    },
    onSuccess: (assertion) => {
      setCommitted(assertion);
      reset({
        unit_id: "",
        event_type: CUSTODY_EVENT_TYPES[0],
        occurred_at: nowForInput(),
        adapter_id: "consola-web",
        evidence_uri: "",
        evidence_sha256: "",
      });
    },
  });

  return (
    <div className="mt-6 grid gap-5 xl:grid-cols-[minmax(0,1fr)_360px]">
      <Card>
        <CardHeader className="flex items-center gap-3">
          <div className="grid h-8 w-8 place-items-center rounded-md border border-border bg-[#111418] text-accent">
            <DatabaseZap className="h-4 w-4" />
          </div>
          <div>
            <h2 className="font-semibold">Declarar aserción de custodia</h2>
            <p className="text-xs text-muted">
              Una vez sellada no se puede editar ni borrar.
            </p>
          </div>
        </CardHeader>

        <CardContent>
          {!canWrite && (
            <div className="mb-5 flex gap-3 rounded-md border border-danger/40 bg-danger/10 p-3">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-danger" />
              <div className="text-sm">
                <div className="font-semibold text-danger">Sin credencial de escritura</div>
                <p className="mt-1 text-muted">
                  Este endpoint exige un JWT. Define <code className="font-mono">VITE_DEMO_JWT</code>{" "}
                  con un token generado por <code className="font-mono">generar_token.py</code>, o
                  el backend responderá 401.
                </p>
              </div>
            </div>
          )}

          <form
            className="space-y-5"
            onSubmit={handleSubmit((form) => mutation.mutate(form))}
            noValidate
          >
            <div className="space-y-2">
              <Label htmlFor="unit_id">Identificador de unidad</Label>
              <Input
                id="unit_id"
                className="font-mono"
                placeholder="udi_di:00812345678901/serial:MX-2048-1190"
                {...register("unit_id", { required: "Obligatorio" })}
              />
              <FieldError message={errors.unit_id?.message} />
            </div>

            <div className="grid gap-5 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="event_type">Tipo de evento</Label>
                <Select id="event_type" {...register("event_type", { required: true })}>
                  {CUSTODY_EVENT_TYPES.map((type) => (
                    <option key={type} value={type}>
                      {eventLabel(type)}
                    </option>
                  ))}
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="occurred_at">Ocurrió el</Label>
                <Input
                  id="occurred_at"
                  type="datetime-local"
                  {...register("occurred_at", { required: "Obligatorio" })}
                />
                <FieldError message={errors.occurred_at?.message} />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="adapter_id">Adaptador de origen</Label>
              <Input
                id="adapter_id"
                className="font-mono"
                {...register("adapter_id", { required: "Obligatorio" })}
              />
              <FieldError message={errors.adapter_id?.message} />
            </div>

            <fieldset className="space-y-5 rounded-md border border-border p-4">
              <legend className="px-2 font-mono text-[10px] uppercase tracking-[0.08em] text-[#66707B]">
                Evidencia (opcional)
              </legend>

              <div className="space-y-2">
                <Label htmlFor="evidence_uri">URI</Label>
                <Input
                  id="evidence_uri"
                  className="font-mono"
                  placeholder="s3://actas/2026/acta-recepcion.pdf"
                  {...register("evidence_uri")}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="evidence_sha256">SHA-256</Label>
                <Input
                  id="evidence_sha256"
                  className="font-mono"
                  placeholder="64 caracteres hexadecimales"
                  {...register("evidence_sha256", {
                    pattern: {
                      value: /^([a-fA-F0-9]{64})?$/,
                      message: "Debe ser un digest hexadecimal de 64 caracteres",
                    },
                  })}
                />
                <FieldError message={errors.evidence_sha256?.message} />
              </div>
            </fieldset>

            {mutation.isError && (
              <p
                role="alert"
                className="rounded-md border border-danger/40 bg-danger/10 px-3 py-2 text-sm text-danger"
              >
                {mutation.error instanceof Error
                  ? mutation.error.message
                  : "No se pudo registrar la aserción."}
              </p>
            )}

            <Button type="submit" variant="primary" disabled={mutation.isPending}>
              {mutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Sellando
                </>
              ) : (
                <>
                  <DatabaseZap className="h-4 w-4" />
                  Sellar en el registro
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      <div className="space-y-5">
        {committed ? (
          <Card className="border-success/40">
            <CardHeader className="flex items-center gap-3">
              <CheckCircle2 className="h-4 w-4 text-success" />
              <h3 className="font-semibold">Aserción sellada</h3>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <Row label="claim_id" value={committed.claim_id} />
              <Row label="unidad" value={committed.unit_id} />
              <Row label="evento" value={eventLabel(committed.event_type)} />
              <Row label="ocurrió el" value={formatInstant(committed.occurred_at)} />
              <Row label="versión de stream" value={String(committed.stream_version)} />
              <Row
                label="posición global"
                value={committed.global_position.toLocaleString("es")}
              />

              <Link
                to={`/app/trazabilidad?unidad=${encodeURIComponent(committed.unit_id)}`}
                className="mt-2 inline-flex text-sm text-accent underline underline-offset-4"
              >
                Ver la cadena completa
              </Link>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className="space-y-3 py-6 text-sm text-muted">
              <Badge tone="accent">append-only</Badge>
              <p className="leading-relaxed">
                Cada declaración se añade al final del registro y queda sellada con su posición
                global y versión de stream. No existe operación de edición ni de borrado.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

function FieldError({ message }: { message?: string }) {
  if (!message) return null;
  return <p className="text-xs text-danger">{message}</p>;
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="font-mono text-[10px] uppercase tracking-[0.08em] text-[#66707B]">
        {label}
      </div>
      <div className="mt-0.5 break-all font-mono text-xs">{value}</div>
    </div>
  );
}
