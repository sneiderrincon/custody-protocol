import { useForm } from "react-hook-form";
import { motion } from "framer-motion";
import { Search, ShieldCheck } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Badge } from "../components/ui/badge";
import type { CustodyEvent, DeviceSnapshot } from "../types/custody";

type LookupForm = { unitId: string };

export function LookupPage({
  snapshot,
  events,
  unitId,
  onLookup,
}: {
  snapshot: DeviceSnapshot;
  events: CustodyEvent[];
  unitId: string;
  onLookup: (unitId: string) => void;
}) {
  const { register, handleSubmit } = useForm<LookupForm>({ defaultValues: { unitId } });
  const latest = events[events.length - 1];

  return (
    <div className="grid gap-5 xl:grid-cols-[minmax(0,0.9fr)_minmax(460px,1.1fr)]">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2 text-sm font-semibold">
            <Search className="h-4 w-4 text-accent" />
            Device custody lookup
          </div>
        </CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={handleSubmit((values) => onLookup(values.unitId))}>
            <div className="space-y-2">
              <Label htmlFor="unitId">UDI-DI / serial / unit_id</Label>
              <Input id="unitId" className="font-mono" {...register("unitId", { required: true })} />
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <Button type="submit" variant="primary">
                <Search className="h-4 w-4" />
                Resolve custody
              </Button>
              <Badge>read-only</Badge>
              <Badge tone="accent">forensic</Badge>
              <Badge className="font-mono">exact stream</Badge>
            </div>
          </form>
        </CardContent>
      </Card>

      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.28 }}>
        <Card className="overflow-hidden">
          <CardHeader className="flex flex-row items-start justify-between gap-4">
            <div>
              <div className="mb-1 text-sm font-semibold">{snapshot.deviceName}</div>
              <div className="break-all font-mono text-xs text-muted">{snapshot.unitId}</div>
            </div>
            <Badge tone="success">verified</Badge>
          </CardHeader>
          <CardContent className="grid gap-0 p-0 sm:grid-cols-2">
            {[
              ["Manufacturer", snapshot.manufacturer],
              ["Current owner", snapshot.currentOwner],
              ["Location", snapshot.currentLocation],
              ["Current status", snapshot.currentStatus],
              ["Last event", latest.eventType],
              ["Last update", snapshot.lastUpdate],
              ["stream_version", String(snapshot.streamVersion)],
              ["global_position", String(snapshot.globalPosition)],
            ].map(([label, value]) => (
              <div key={label} className="min-w-0 border-b border-[#1E232A] p-4 even:sm:border-l">
                <div className="mb-1 text-xs text-[#66707B]">{label}</div>
                <div className="break-words text-sm font-semibold text-white">{value}</div>
              </div>
            ))}
          </CardContent>
          <div className="flex items-center gap-2 border-t border-[#1E232A] px-4 py-3 text-xs text-muted">
            <ShieldCheck className="h-4 w-4 text-success" />
            Projection replayed from immutable event log. No mutable source of truth is displayed.
          </div>
        </Card>
      </motion.div>
    </div>
  );
}
