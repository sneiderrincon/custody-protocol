import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Loader2, Settings, UserRound, HeartPulse } from "lucide-react";
import { AppShell, type ViewId } from "./layouts/AppShell";
import { PageHeader } from "./components/PageHeader";
import { DashboardPage } from "./pages/DashboardPage";
import { DeclarePage } from "./pages/DeclarePage";
import { HistoryPage } from "./pages/HistoryPage";
import { LookupPage } from "./pages/LookupPage";
import { StatePage } from "./pages/StatePage";
import { useDeviceCustody } from "./hooks/useDeviceCustody";
import { snapshot as defaultSnapshot } from "./services/custodyService";
import { Badge } from "./components/ui/badge";
import { Card, CardContent, CardHeader } from "./components/ui/card";

const headers: Record<ViewId, { eyebrow: string; title: string; copy: string; badges: Array<{ label: string; tone?: "default" | "accent" | "success" | "danger" }> }> = {
  dashboard: {
    eyebrow: "Operational command center",
    title: "Dashboard de trazabilidad Kernel.",
    copy: "Vista ejecutiva para monitorear dispositivos, assertions append-only, salud del protocolo y eventos regulatorios en tiempo real.",
    badges: [
      { label: "enterprise" },
      { label: "server online", tone: "success" },
      { label: "immutable", tone: "accent" },
    ],
  },
  devices: {
    eyebrow: "Medical device registry",
    title: "Dispositivos bajo monitoreo.",
    copy: "Inventario operacional de dispositivos médicos con propietario, estado de custodia, ubicación y versión de stream.",
    badges: [
      { label: "cards" },
      { label: "tables" },
      { label: "verified", tone: "success" },
    ],
  },
  search: {
    eyebrow: "Forensic retrieval",
    title: "Consulta la cadena de custodia completa de un dispositivo médico.",
    copy: "Un espacio operacional para fabricantes, distribuidores, hospitales y auditores regulatorios. La experiencia prioriza confianza, trazabilidad e integridad append-only.",
    badges: [
      { label: "read-only" },
      { label: "forensic", tone: "accent" },
      { label: "verified", tone: "success" },
    ],
  },
  custody: {
    eyebrow: "Chain of custody",
    title: "Timeline inmutable de eventos aceptados.",
    copy: "Cada assertion conserva actor, fecha, claim_id, stream_version y global_position sin caer en una tabla CRUD. La línea vertical comunica continuidad de custodia.",
    badges: [
      { label: "append-only", tone: "accent" },
      { label: "5 assertions", tone: "success" },
    ],
  },
  declare: {
    eyebrow: "Immutable event intake",
    title: "Nueva Aserción con preview vivo y validación visual.",
    copy: "Formulario por secciones para declarar eventos de fabricación, distribución, recepción o disposición. El JSON representa el cuerpo que se anexará al stream.",
    badges: [
      { label: "schema valid", tone: "success" },
      { label: "fail-closed" },
      { label: "append-only", tone: "accent" },
    ],
  },
  settings: {
    eyebrow: "Protocol configuration",
    title: "Configuración del workspace.",
    copy: "Políticas de integridad, retención de evidencia, permisos regulatorios y parámetros de conexión del protocolo.",
    badges: [{ label: "admin" }, { label: "fail-closed", tone: "accent" }],
  },
  health: {
    eyebrow: "System observability",
    title: "Health del servidor y servicios criticos.",
    copy: "Estado del BFF, backend FastAPI, base de datos, Redis y canal de auditoria.",
    badges: [{ label: "healthy", tone: "success" }, { label: "24ms" }],
  },
  user: {
    eyebrow: "Session identity",
    title: "Usuario y permisos.",
    copy: "Contexto del actor autenticado, organizacion, permisos UX y rol regulatorio efectivo.",
    badges: [{ label: "Manufacturer" }, { label: "active", tone: "success" }],
  },
};

export default function App() {
  const [activeView, setActiveView] = useState<ViewId>("dashboard");
  const [unitId, setUnitId] = useState(defaultSnapshot.unitId);
  const custodyQuery = useDeviceCustody(unitId);
  const data = custodyQuery.data;

  return (
    <AppShell activeView={activeView} onViewChange={setActiveView}>
      <PageHeader {...headers[activeView]} />
      {custodyQuery.isLoading || !data ? (
        <Card className="grid min-h-64 place-items-center p-8 text-muted">
          <div className="flex items-center gap-3">
            <Loader2 className="h-4 w-4 animate-spin text-accent" />
            Resolving custody stream
          </div>
        </Card>
      ) : (
        <AnimatePresence mode="wait">
          <motion.div
            key={activeView}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.22 }}
          >
            {activeView === "dashboard" && <DashboardPage snapshot={data.snapshot} events={data.events} />}
            {activeView === "devices" && <StatePage snapshot={data.snapshot} />}
            {activeView === "search" && (
              <LookupPage snapshot={data.snapshot} events={data.events} unitId={unitId} onLookup={setUnitId} />
            )}
            {activeView === "custody" && <HistoryPage events={data.events} />}
            {activeView === "declare" && <DeclarePage />}
            {activeView === "settings" && <UtilityPanel icon={Settings} title="Configuración" rows={["JWT provider: BFF", "Session store: Redis", "Evidence retention: 10 years", "RBAC: fail-closed"]} />}
            {activeView === "health" && <UtilityPanel icon={HeartPulse} title="Health" rows={["BFF: online", "FastAPI: online", "Postgres: online", "Audit channel: online"]} success />}
            {activeView === "user" && <UtilityPanel icon={UserRound} title="Usuario" rows={["Actor: act_8F39B2A0", "Role: Manufacturer", "Trust level: REGULATED", "Workspace: Andean Medical Trust Network"]} />}
          </motion.div>
        </AnimatePresence>
      )}
    </AppShell>
  );
}

function UtilityPanel({
  icon: Icon,
  title,
  rows,
  success = false,
}: {
  icon: typeof Settings;
  title: string;
  rows: string[];
  success?: boolean;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div className="flex items-center gap-2 text-sm font-semibold">
          <Icon className="h-4 w-4 text-accent" />
          {title}
        </div>
        <Badge tone={success ? "success" : "accent"}>{success ? "online" : "controlled"}</Badge>
      </CardHeader>
      <CardContent className="grid gap-3 md:grid-cols-2">
        {rows.map((row) => (
          <div key={row} className="rounded-md border border-[#1E232A] bg-[#111418] p-3 text-sm text-muted">
            {row}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
