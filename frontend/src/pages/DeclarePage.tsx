import type { ReactNode } from "react";
import { useMemo } from "react";
import { useForm } from "react-hook-form";
import { Code2, DatabaseZap, FileCheck2, Fingerprint, ShieldCheck } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Select } from "../components/ui/select";
import { Textarea } from "../components/ui/textarea";
import { Badge } from "../components/ui/badge";

type AssertionForm = {
  claimId: string;
  unitId: string;
  eventType: string;
  occurredAt: string;
  actorId: string;
  adapterId: string;
  owner: string;
  location: string;
  status: string;
  notes: string;
  evidenceUri: string;
  sha256: string;
};

export function DeclarePage() {
  const { register, watch } = useForm<AssertionForm>({
    defaultValues: {
      claimId: "clm_018fb6b2-47a6-7e18-91e1-3a6dd8fb3a21",
      unitId: "udi_di:00812345678901/serial:MX-2048-1190",
      eventType: "RECEIVED",
      occurredAt: "2026-08-05T14:38",
      actorId: "act_8F39B2A0-3E5C-42D7-9B63-45E1B9A12F7C",
      adapterId: "bff.medical-device.intake.v1",
      owner: "Hospital Universitario San Ignacio",
      location: "Bogota DC / OR-7 sterile storage",
      status: "IN_CUSTODY",
      notes: "Temperature range verified, tamper seal intact, sterile pouch scanned at receiving bay.",
      evidenceUri: "s3://custody-evidence/2026/08/receiving-slip-1190.pdf",
      sha256: "6f38a9c11d4478e8b6af746d9a6c3e5c2f901be21a1bbfb3d4410972c47fd940",
    },
  });

  const values = watch();
  const preview = useMemo(
    () => ({
      claim_id: values.claimId,
      unit_id: values.unitId,
      event_type: values.eventType,
      occurred_at: new Date(values.occurredAt || Date.now()).toISOString(),
      provenance: {
        actor_id: values.actorId,
        adapter_id: values.adapterId,
        evidence: [{ uri: values.evidenceUri, sha256: values.sha256 }],
      },
      payload: {
        attributes: [
          { key: "current_owner", value: values.owner },
          { key: "current_location", value: values.location },
          { key: "current_status", value: values.status },
          { key: "notes", value: values.notes },
        ],
      },
    }),
    [values],
  );

  return (
    <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_420px]">
      <div className="space-y-4">
        <FormSection icon={Fingerprint} title="Identity" kicker="claim envelope">
          <Field className="sm:col-span-2" label="claim_id">
            <Input className="font-mono" {...register("claimId")} />
          </Field>
          <Field label="unit_id">
            <Input className="font-mono" {...register("unitId")} />
          </Field>
          <Field label="event_type">
            <Select {...register("eventType")}>
              <option>MANUFACTURED</option>
              <option>QC_RELEASED</option>
              <option>DISPATCHED</option>
              <option>RECEIVED</option>
              <option>STERILIZED</option>
              <option>RECALLED</option>
            </Select>
          </Field>
        </FormSection>

        <FormSection icon={DatabaseZap} title="Event" kicker="custody mutation">
          <Field label="occurred_at">
            <Input type="datetime-local" {...register("occurredAt")} />
          </Field>
          <Field label="current_status">
            <Select {...register("status")}>
              <option>IN_CUSTODY</option>
              <option>RELEASED</option>
              <option>QUARANTINED</option>
              <option>RECALLED</option>
            </Select>
          </Field>
        </FormSection>

        <FormSection icon={ShieldCheck} title="Provenance" kicker="who declared it">
          <Field label="actor_id">
            <Input className="font-mono" {...register("actorId")} />
          </Field>
          <Field label="adapter_id">
            <Input className="font-mono" {...register("adapterId")} />
          </Field>
        </FormSection>

        <FormSection icon={FileCheck2} title="Payload" kicker="state deltas">
          <Field label="current_owner">
            <Input {...register("owner")} />
          </Field>
          <Field label="location">
            <Input {...register("location")} />
          </Field>
          <Field className="sm:col-span-2" label="payload_notes">
            <Textarea {...register("notes")} />
          </Field>
        </FormSection>

        <FormSection icon={Code2} title="Evidence" kicker="hash anchored">
          <Field label="evidence_uri">
            <Input className="font-mono" {...register("evidenceUri")} />
          </Field>
          <Field label="sha256">
            <Input className="font-mono" {...register("sha256")} />
          </Field>
          <div className="flex flex-wrap items-center gap-2 sm:col-span-2">
            <Button variant="primary" type="button">
              <ShieldCheck className="h-4 w-4" />
              Declare assertion
            </Button>
            <Button type="button">
              <Code2 className="h-4 w-4" />
              Validate payload
            </Button>
            <span className="text-xs text-[#66707B]">Every accepted declaration appends a new event.</span>
          </div>
        </FormSection>
      </div>

      <Card className="sticky top-5 overflow-hidden self-start">
        <CardHeader className="flex flex-row items-center justify-between">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <Code2 className="h-4 w-4 text-accent" />
            Live JSON Preview
          </div>
          <Badge tone="accent">real time</Badge>
        </CardHeader>
        <pre className="max-h-[680px] overflow-auto p-4 font-mono text-xs leading-6 text-[#C9D1D9]">
          {JSON.stringify(preview, null, 2)}
        </pre>
      </Card>
    </div>
  );
}

function FormSection({
  icon: Icon,
  title,
  kicker,
  children,
}: {
  icon: typeof ShieldCheck;
  title: string;
  kicker: string;
  children: ReactNode;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-sm font-semibold">
          <Icon className="h-4 w-4 text-accent" />
          {title}
        </div>
        <div className="font-mono text-[10px] uppercase tracking-[0.08em] text-[#66707B]">{kicker}</div>
      </CardHeader>
      <CardContent className="grid gap-4 sm:grid-cols-2">{children}</CardContent>
    </Card>
  );
}

function Field({ label, className, children }: { label: string; className?: string; children: ReactNode }) {
  return (
    <div className={className}>
      <Label>{label}</Label>
      <div className="mt-2">{children}</div>
    </div>
  );
}
