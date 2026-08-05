import { Clock3, Factory, Layers3, MapPin, ShieldCheck, UserRound } from "lucide-react";
import { motion } from "framer-motion";
import { Card } from "../components/ui/card";
import type { DeviceSnapshot } from "../types/custody";

const cards = [
  { key: "currentOwner", label: "Current owner", icon: UserRound },
  { key: "currentLocation", label: "Current location", icon: MapPin },
  { key: "currentStatus", label: "Current status", icon: ShieldCheck },
  { key: "lastEvent", label: "Last event", icon: Layers3 },
  { key: "lastUpdate", label: "Last update", icon: Clock3 },
] as const;

export function StatePage({ snapshot }: { snapshot: DeviceSnapshot }) {
  return (
    <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_340px]">
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
        {cards.map((item, index) => {
          const Icon = item.icon;
          return (
            <motion.div key={item.key} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.04 }}>
              <Card className="flex min-h-40 flex-col justify-between p-4">
                <div className="grid h-9 w-9 place-items-center rounded-md border border-border bg-[#111418] text-accent">
                  <Icon className="h-4 w-4" />
                </div>
                <div>
                  <div className="text-xs text-[#66707B]">{item.label}</div>
                  <div className="mt-2 break-words text-base font-semibold">{String(snapshot[item.key])}</div>
                </div>
              </Card>
            </motion.div>
          );
        })}
      </div>

      <Card className="p-4">
        <div className="mb-4 flex items-center gap-2 text-sm font-semibold">
          <Factory className="h-4 w-4 text-accent" />
          Snapshot integrity
        </div>
        <div className="space-y-3 text-sm leading-6 text-muted">
          <CheckLine text={`State projection replayed from stream version ${snapshot.streamVersion}.`} />
          <CheckLine text="Evidence digest matches declared SHA-256." />
          <CheckLine text="Regulatory access labels include INVIMA, FDA and hospital auditor roles." />
          <CheckLine text="No mutable correction event is present in the active custody window." />
        </div>
      </Card>
    </div>
  );
}

function CheckLine({ text }: { text: string }) {
  return (
    <div className="flex gap-2">
      <ShieldCheck className="mt-1 h-4 w-4 flex-none text-success" />
      <span>{text}</span>
    </div>
  );
}
