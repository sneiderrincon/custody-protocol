import type { ReactNode } from "react";
import {
  Activity,
  Cable,
  DatabaseZap,
  FileClock,
  Gauge,
  HeartPulse,
  Laptop,
  Moon,
  Search,
  Settings,
  ShieldCheck,
  UserRound,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { cn } from "../lib/utils";

export type ViewId = "dashboard" | "devices" | "custody" | "declare" | "search" | "settings" | "health" | "user";

const navItems: Array<{ id: ViewId; label: string; icon: typeof Search }> = [
  { id: "dashboard", label: "Dashboard", icon: Gauge },
  { id: "devices", label: "Dispositivos", icon: Laptop },
  { id: "custody", label: "Cadena de Custodia", icon: FileClock },
  { id: "declare", label: "Nueva Aserción", icon: DatabaseZap },
  { id: "search", label: "Buscar", icon: Search },
  { id: "settings", label: "Configuración", icon: Settings },
  { id: "health", label: "Health", icon: HeartPulse },
  { id: "user", label: "Usuario", icon: UserRound },
];

export function AppShell({
  activeView,
  onViewChange,
  children,
}: {
  activeView: ViewId;
  onViewChange: (view: ViewId) => void;
  children: ReactNode;
}) {
  const activeLabel = navItems.find((item) => item.id === activeView)?.label ?? "Dashboard";

  return (
    <div className="min-h-screen bg-background text-white lg:grid lg:grid-cols-[280px_minmax(0,1fr)]">
      <aside className="border-b border-[#1E232A] bg-[#0D1013] p-4 lg:sticky lg:top-0 lg:h-screen lg:border-b-0 lg:border-r">
        <div className="flex items-center gap-3 px-2 pb-5">
          <div className="grid h-9 w-9 place-items-center rounded-lg border border-border bg-panel text-accent">
            <ShieldCheck className="h-4 w-4" />
          </div>
          <div>
            <div className="font-semibold">Kernel</div>
            <div className="font-mono text-[11px] text-[#66707B]">medical trace protocol</div>
          </div>
        </div>

        <div className="mb-5 rounded-lg border border-[#1E232A] bg-panel p-3">
          <div className="mb-2 flex items-center justify-between gap-3">
            <span className="font-mono text-[10px] uppercase tracking-[0.08em] text-[#66707B]">Network</span>
            <Badge tone="success">Verified</Badge>
          </div>
          <div className="mb-2 text-sm font-semibold">Andean Medical Trust Network</div>
          <div className="flex items-center gap-2 text-xs text-muted">
            <span className="h-1.5 w-1.5 rounded-full bg-success" />
            INVIMA/FDA audit channel active
          </div>
        </div>

        <nav aria-label="Primary" className="space-y-1">
          <div className="px-2 pb-2 pt-3 font-mono text-[10px] uppercase tracking-[0.08em] text-[#66707B]">Navigation</div>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => onViewChange(item.id)}
                className={cn(
                  "flex w-full items-center gap-3 rounded-md border border-transparent px-3 py-2.5 text-left text-sm text-muted transition-colors hover:bg-[#111419] hover:text-white",
                  activeView === item.id && "border-border bg-panel text-white",
                )}
              >
                <Icon className={cn("h-4 w-4 text-[#66707B]", activeView === item.id && "text-accent")} />
                {item.label}
              </button>
            );
          })}
        </nav>

        <div className="mt-8 border-t border-[#1E232A] pt-4 lg:absolute lg:bottom-5 lg:left-4 lg:right-4 lg:mt-0">
          {[
            ["stream health", "99.99%"],
            ["global_position", "8,214,605"],
            ["hash policy", "SHA-256"],
          ].map(([label, value]) => (
            <div key={label} className="mb-2 flex items-center justify-between font-mono text-[11px] text-[#66707B]">
              <span>{label}</span>
              <span className="text-muted">{value}</span>
            </div>
          ))}
        </div>
      </aside>

      <main className="min-w-0 px-4 pb-10 pt-4 sm:px-6 lg:px-8 lg:pt-6">
        <header className="flex flex-col gap-4 border-b border-[#1E232A] pb-5 md:flex-row md:items-center md:justify-between">
          <div className="min-w-0">
            <div className="mb-2 flex items-center gap-2 text-sm text-muted">
              <ShieldCheck className="h-4 w-4" />
              <span>Kernel</span>
              <span>/</span>
              <span>Traceability</span>
              <span>/</span>
              <strong className="text-white">{activeLabel}</strong>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone="success">Servidor online</Badge>
              <Badge className="font-mono">latency 24ms</Badge>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Button variant="default" size="sm">
              <Cable className="h-4 w-4" />
              Conexión
            </Button>
            <Button variant="ghost" size="sm">
              <Moon className="h-4 w-4" />
              Modo oscuro
            </Button>
            <Badge className="font-mono">actor: act_8F39B2A0</Badge>
            <Badge>Usuario</Badge>
            <Button variant="ghost" size="sm" aria-label="Audit mode">
              <Activity className="h-4 w-4" />
            </Button>
          </div>
        </header>
        {children}
      </main>
    </div>
  );
}
