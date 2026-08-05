import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { FileJson, LockKeyhole, MapPin } from "lucide-react";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Card } from "../components/ui/card";
import type { CustodyEvent } from "../types/custody";

export function HistoryPage({ events }: { events: CustodyEvent[] }) {
  const [openClaim, setOpenClaim] = useState<string | null>(null);

  return (
    <div className="relative pl-8">
      <div className="absolute bottom-3 left-[11px] top-3 w-px bg-border" />
      <div className="space-y-4">
        {events.map((event, index) => {
          const open = openClaim === event.claimId;
          return (
            <motion.article
              key={event.claimId}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.04, duration: 0.24 }}
              className="relative"
            >
              <div className="absolute -left-[31px] top-5 h-3 w-3 rounded-full border-2 border-accent bg-background" />
              <Card className="p-4">
                <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <LockKeyhole className="h-4 w-4 text-accent" />
                      <h2 className="text-base font-semibold">{event.eventType}</h2>
                      <Badge tone={event.status === "accepted" ? "success" : "accent"}>{event.status}</Badge>
                    </div>
                    <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-muted">
                      <span>{event.actor}</span>
                      <span>/</span>
                      <span>{event.occurredAt}</span>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => setOpenClaim(open ? null : event.claimId)}>
                    <FileJson className="h-4 w-4" />
                    {open ? "Ocultar JSON" : "Ver JSON"}
                  </Button>
                </div>

                <div className="mt-4 grid gap-3 md:grid-cols-3">
                  <Fact label="claim_id" value={event.claimId} mono />
                  <Fact label="stream_version" value={String(event.streamVersion)} mono />
                  <Fact label="global_position" value={String(event.globalPosition)} mono />
                </div>

                <div className="mt-3 flex items-center gap-2 text-xs text-muted">
                  <MapPin className="h-4 w-4 text-[#66707B]" />
                  {event.location}
                </div>

                <AnimatePresence>
                  {open && (
                    <motion.pre
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      className="mt-4 overflow-hidden rounded-md border border-[#1E232A] bg-[#0F1216] p-3 font-mono text-xs leading-6 text-[#C9D1D9]"
                    >
                      {JSON.stringify(event, null, 2)}
                    </motion.pre>
                  )}
                </AnimatePresence>
              </Card>
            </motion.article>
          );
        })}
      </div>
    </div>
  );
}

function Fact({ label, value, mono = false }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="min-w-0 rounded-md border border-[#1E232A] bg-[#111418] p-3">
      <div className="mb-1 text-xs text-[#66707B]">{label}</div>
      <div className={mono ? "break-all font-mono text-xs text-white" : "break-words text-sm text-white"}>{value}</div>
    </div>
  );
}
