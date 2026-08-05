import { useEffect, useMemo, useState } from "react";
import type { LucideIcon } from "lucide-react";
import { Activity, Clock3, FileClock, Fingerprint, HeartPulse, Laptop, MapPin, ShieldCheck } from "lucide-react";
import { motion } from "framer-motion";
import { Badge } from "../components/ui/badge";
import { Card, CardContent, CardHeader } from "../components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../components/ui/table";
import type { CustodyEvent, CustodyEventType, DeviceSnapshot } from "../types/custody";

type DeviceRow = {
  id: string;
  device: string;
  owner: string;
  status: string;
  lastEvent: CustodyEventType;
  stream: number;
  location: string;
};

const deviceRows: DeviceRow[] = [
  {
    id: "MX-2048-1190",
    device: "Sterile implantable infusion port",
    owner: "Hospital Universitario San Ignacio",
    status: "In custody",
    lastEvent: "RECEIVED",
    stream: 18,
    location: "Bogota DC / OR-7 sterile storage",
  },
  {
    id: "CM-910-4421",
    device: "Cardiac monitor CM-910",
    owner: "Clinica del Country",
    status: "Released",
    lastEvent: "QC_RELEASED",
    stream: 31,
    location: "Bogota DC / ICU-2",
  },
  {
    id: "IPX-44-7710",
    device: "Infusion pump IPX-44",
    owner: "Cold Chain Distributor SAS",
    status: "In transit",
    lastEvent: "DISPATCHED",
    stream: 12,
    location: "Bogota bonded logistics hub",
  },
  {
    id: "SK-77-9012",
    device: "Surgical kit SK-77",
    owner: "Fundacion Santa Fe",
    status: "Sterilized",
    lastEvent: "STERILIZED",
    stream: 9,
    location: "Bogota DC / CSSD",
  },
];

export function DashboardPage({ snapshot, events }: { snapshot: DeviceSnapshot; events: CustodyEvent[] }) {
  const [tick, setTick] = useState(0);

  useEffect(() => {
    const timer = window.setInterval(() => setTick((value) => value + 1), 3200);
    return () => window.clearInterval(timer);
  }, []);

  const liveEvents = useMemo(() => {
    const generated = Array.from({ length: Math.min(tick, 6) }, (_, index): CustodyEvent => {
      const device = deviceRows[(index + 1) % deviceRows.length];
      const type: CustodyEventType[] = ["IN_TRANSIT_SCAN", "RECEIVED", "QC_RELEASED", "DISPATCHED", "STERILIZED", "RECEIVED"];
      return {
        claimId: `clm_live_${String(8214606 + index)}`,
        unitId: `udi_di:00812345678901/serial:${device.id}`,
        eventType: type[index],
        actor: index % 2 === 0 ? "Kernel BFF Intake" : device.owner,
        actorType: index % 2 === 0 ? "Distributor" : "Hospital",
        occurredAt: `2026-08-05 ${String(14 + Math.floor(index / 2)).padStart(2, "0")}:${String(42 + index * 3).padStart(2, "0")} UTC`,
        streamVersion: device.stream + index + 1,
        globalPosition: 8214606 + index,
        location: device.location,
        evidenceDigest: "sha256:" + `6f38${index}`.padEnd(16, "0"),
        status: index === 2 ? "review" : "accepted",
      };
    });
    return [...events, ...generated];
  }, [events, tick]);

  const recent = liveEvents.slice(-5).reverse();
  const pending = liveEvents.filter((event) => event.status === "review" || event.status === "quarantined").length;
  const today = liveEvents.filter((event) => event.occurredAt.startsWith("2026-08-05")).length;
  const integrity = liveEvents.some((event) => event.status === "quarantined") ? "Attention" : "100%";
  const health = tick % 5 === 4 ? "Degraded" : "Online";
  const days = ["Ago 01", "Ago 02", "Ago 03", "Ago 04", "Ago 05"];
  const dailyCounts = days.map((label, index) => ({
    label,
    value: liveEvents.filter((event) => event.occurredAt.startsWith(`2026-08-0${index + 1}`)).length,
  }));
  const maxCount = Math.max(...dailyCounts.map((day) => day.value), 1);
  const latestDevices = deviceRows.map((device, index) => ({
    ...device,
    stream: device.stream + Math.max(0, tick - index),
    status: index === tick % deviceRows.length ? "Active update" : device.status,
  }));

  const metrics: Array<{ label: string; value: string; detail: string; icon: LucideIcon; tone?: "default" | "accent" | "success" | "danger" }> = [
    { label: "Dispositivos registrados", value: String(1284 + Math.floor(tick / 2)), detail: "4 con actividad reciente", icon: Laptop },
    { label: "Aserciones", value: liveEvents.length.toLocaleString("en-US"), detail: "append-only log activo", icon: FileClock },
    { label: "Eventos hoy", value: String(today), detail: "actualiza en tiempo real", icon: Activity, tone: "accent" },
    { label: "Eventos pendientes", value: String(pending), detail: "requieren revision operacional", icon: Clock3, tone: pending > 0 ? "accent" : "success" },
    { label: "Integridad", value: integrity, detail: "hash/evidence chain valid", icon: Fingerprint, tone: "success" },
    { label: "Health API", value: health, detail: health === "Online" ? "BFF + FastAPI OK" : "latencia elevada", icon: HeartPulse, tone: health === "Online" ? "success" : "accent" },
  ];

  return (
    <div className="grid gap-5">
      <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-6">
        {metrics.map(({ label, value, detail, icon: Icon, tone }, index) => (
          <motion.div key={label} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.04 }}>
            <Card className="p-4">
              <div className="mb-6 flex items-center justify-between">
                <div className="grid h-9 w-9 place-items-center rounded-md border border-border bg-[#111418] text-accent">
                  <Icon className="h-4 w-4" />
                </div>
                <Badge tone={tone ?? "default"}>{tone === "success" ? "clean" : "live"}</Badge>
              </div>
              <div className="text-xs text-[#66707B]">{label}</div>
              <motion.div key={value} initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }} className="mt-2 text-2xl font-semibold">
                {value}
              </motion.div>
              <div className="mt-1 text-xs text-muted">{detail}</div>
            </Card>
          </motion.div>
        ))}
      </section>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <div className="text-sm font-semibold">Eventos por día</div>
            <div className="mt-1 text-xs text-muted">Volumen diario calculado desde el stream de eventos</div>
          </div>
          <Badge tone="accent">real time</Badge>
        </CardHeader>
        <CardContent>
          <div className="grid h-64 grid-cols-5 items-end gap-3">
            {dailyCounts.map((day) => (
              <div key={day.label} className="flex h-full min-w-0 flex-col justify-end gap-2">
                <motion.div
                  animate={{ height: `${Math.max(8, (day.value / maxCount) * 100)}%` }}
                  transition={{ duration: 0.45 }}
                  className="rounded-t-md border border-[#514028] bg-[#2C2419]"
                >
                  <div className="pt-2 text-center font-mono text-xs text-accent">{day.value}</div>
                </motion.div>
                <div className="truncate text-center font-mono text-xs text-[#66707B]">{day.label}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="text-sm font-semibold">Timeline reciente</div>
          <div className="mt-1 text-xs text-muted">Ultimos eventos recibidos por el protocolo Kernel</div>
        </CardHeader>
        <CardContent>
          <div className="relative pl-7">
            <div className="absolute bottom-2 left-[9px] top-2 w-px bg-border" />
            <div className="space-y-3">
              {recent.map((event) => (
                <motion.div
                  key={event.claimId}
                  layout
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="relative rounded-md border border-[#1E232A] bg-[#111418] p-3"
                >
                  <div className="absolute -left-[23px] top-4 h-2.5 w-2.5 rounded-full border-2 border-accent bg-background" />
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-semibold">{event.eventType}</span>
                        <Badge tone={event.status === "accepted" ? "success" : "accent"}>{event.status}</Badge>
                      </div>
                      <div className="mt-1 flex items-center gap-1.5 text-xs text-muted">
                        <MapPin className="h-3.5 w-3.5" />
                        {event.location}
                      </div>
                    </div>
                    <div className="font-mono text-xs text-muted">{event.claimId}</div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      <section className="grid gap-5 xl:grid-cols-[minmax(0,1.25fr)_380px]">
        <Card className="overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <div className="text-sm font-semibold">Últimos dispositivos</div>
              <div className="mt-1 text-xs text-muted">Registros más recientes y su estado operativo</div>
            </div>
            <Badge tone="accent">critical inventory</Badge>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Device</TableHead>
                  <TableHead>Owner</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Stream</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {latestDevices.map((device) => (
                  <TableRow key={device.id}>
                    <TableCell>
                      <div className="font-medium">{device.device}</div>
                      <div className="mt-1 font-mono text-xs text-[#66707B]">{device.id}</div>
                    </TableCell>
                    <TableCell className="text-muted">{device.owner}</TableCell>
                    <TableCell>
                      <Badge tone={device.status === "Active update" || device.status === "In custody" || device.status === "Sterilized" ? "success" : "default"}>{device.status}</Badge>
                    </TableCell>
                    <TableCell className="text-right font-mono text-xs">v{device.stream}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="text-sm font-semibold">Detalles</div>
            <div className="mt-1 break-all font-mono text-xs text-muted">{snapshot.unitId}</div>
          </CardHeader>
          <CardContent className="space-y-4">
            {[
              ["Current owner", snapshot.currentOwner],
              ["Current location", snapshot.currentLocation],
              ["Last event", recent[0]?.eventType ?? snapshot.lastEvent],
              ["global_position", String(recent[0]?.globalPosition ?? snapshot.globalPosition)],
            ].map(([label, value]) => (
              <div key={label} className="rounded-md border border-[#1E232A] bg-[#111418] p-3">
                <div className="text-xs text-[#66707B]">{label}</div>
                <div className="mt-1 break-words text-sm font-semibold">{value}</div>
              </div>
            ))}
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
