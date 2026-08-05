import { useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import {
  Boxes,
  ClipboardCheck,
  DatabaseZap,
  FileClock,
  FileSpreadsheet,
  Laptop,
  LogOut,
  Menu,
  ScrollText,
  ShieldCheck,
  Stethoscope,
  X,
} from "lucide-react";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { useSession } from "../auth/SessionContext";
import { useHealth } from "../hooks/useHealth";
import { cn } from "../lib/utils";

interface NavItem {
  to: string;
  label: string;
  icon: typeof Boxes;
  /** Sin backend hoy: se navega, pero la pantalla lo dice explicitamente. */
  pending?: boolean;
}

const operationalItems: NavItem[] = [
  { to: "/app/trazabilidad", label: "Trazabilidad", icon: FileClock },
  { to: "/app/catalogo", label: "Catálogo", icon: Boxes },
  { to: "/app/declarar", label: "Declarar evento", icon: DatabaseZap },
];

const pendingItems: NavItem[] = [
  { to: "/app/inventario", label: "Inventario", icon: Laptop, pending: true },
  { to: "/app/cargas", label: "Cargas masivas", icon: FileSpreadsheet, pending: true },
  { to: "/app/auditoria", label: "Auditoría", icon: ScrollText, pending: true },
  { to: "/app/uso-clinico", label: "Uso clínico", icon: Stethoscope, pending: true },
  { to: "/app/calidad", label: "Calidad y regulatorio", icon: ClipboardCheck, pending: true },
];

const allItems = [...operationalItems, ...pendingItems];

export function AppShell() {
  const { session, logout } = useSession();
  const navigate = useNavigate();
  const location = useLocation();
  const health = useHealth();
  const [isNavOpen, setIsNavOpen] = useState(false);

  const activeLabel =
    allItems.find((item) => location.pathname.startsWith(item.to))?.label ?? "Consola";

  async function handleLogout() {
    await logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="min-h-screen bg-background text-white lg:grid lg:grid-cols-[280px_minmax(0,1fr)]">
      <aside
        className={cn(
          "border-b border-[#1E232A] bg-[#0D1013] p-4 lg:sticky lg:top-0 lg:flex lg:h-screen lg:flex-col lg:border-b-0 lg:border-r",
          !isNavOpen && "hidden lg:flex",
        )}
      >
        <div className="flex items-center gap-3 px-2 pb-5">
          <div className="grid h-9 w-9 place-items-center rounded-lg border border-border bg-panel text-accent">
            <ShieldCheck className="h-4 w-4" />
          </div>
          <div>
            <div className="font-semibold">Kernel</div>
            <div className="font-mono text-[11px] text-[#66707B]">medical trace protocol</div>
          </div>
        </div>

        <nav aria-label="Principal" className="flex-1 space-y-1 overflow-y-auto">
          <NavGroup label="Operación" />
          {operationalItems.map((item) => (
            <NavItemLink key={item.to} item={item} onNavigate={() => setIsNavOpen(false)} />
          ))}

          <NavGroup label="Próximamente" />
          {pendingItems.map((item) => (
            <NavItemLink key={item.to} item={item} onNavigate={() => setIsNavOpen(false)} />
          ))}
        </nav>

        <div className="mt-6 space-y-3 border-t border-[#1E232A] pt-4">
          <div className="flex items-center justify-between gap-3">
            <span className="font-mono text-[10px] uppercase tracking-[0.08em] text-[#66707B]">
              backend
            </span>
            <HealthBadge isPending={health.isPending} isError={health.isError} />
          </div>

          <div className="min-w-0">
            <div className="truncate text-sm font-semibold">{session?.displayName}</div>
            <div className="truncate text-xs text-muted">{session?.email}</div>
            <div
              className="mt-1 truncate font-mono text-[10px] text-[#66707B]"
              title={session?.actorId}
            >
              actor {session?.actorId}
            </div>
          </div>

          <Button variant="ghost" size="sm" className="w-full" onClick={handleLogout}>
            <LogOut className="h-4 w-4" />
            Cerrar sesión
          </Button>
        </div>
      </aside>

      <main className="min-w-0 px-4 pb-10 pt-4 sm:px-6 lg:px-8 lg:pt-6">
        <header className="flex items-center justify-between gap-4 border-b border-[#1E232A] pb-5">
          <div className="flex min-w-0 items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              aria-label={isNavOpen ? "Cerrar navegación" : "Abrir navegación"}
              aria-expanded={isNavOpen}
              onClick={() => setIsNavOpen((open) => !open)}
            >
              {isNavOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
            </Button>

            <div className="flex min-w-0 items-center gap-2 text-sm text-muted">
              <span className="hidden sm:inline">Kernel</span>
              <span className="hidden sm:inline">/</span>
              <strong className="truncate text-white">{activeLabel}</strong>
            </div>
          </div>
        </header>

        <Outlet />
      </main>
    </div>
  );
}

function NavGroup({ label }: { label: string }) {
  return (
    <div className="px-2 pb-2 pt-4 font-mono text-[10px] uppercase tracking-[0.08em] text-[#66707B]">
      {label}
    </div>
  );
}

function NavItemLink({ item, onNavigate }: { item: NavItem; onNavigate: () => void }) {
  const Icon = item.icon;

  return (
    <NavLink
      to={item.to}
      onClick={onNavigate}
      className={({ isActive }) =>
        cn(
          "flex w-full items-center gap-3 rounded-md border border-transparent px-3 py-2.5 text-left text-sm text-muted transition-colors hover:bg-[#111419] hover:text-white",
          isActive && "border-border bg-panel text-white",
        )
      }
    >
      {({ isActive }) => (
        <>
          <Icon className={cn("h-4 w-4 shrink-0 text-[#66707B]", isActive && "text-accent")} />
          <span className="flex-1 truncate">{item.label}</span>
          {item.pending && (
            <span className="font-mono text-[9px] uppercase text-[#66707B]">pend</span>
          )}
        </>
      )}
    </NavLink>
  );
}

function HealthBadge({ isPending, isError }: { isPending: boolean; isError: boolean }) {
  if (isPending) return <Badge>comprobando…</Badge>;
  if (isError) return <Badge tone="danger">sin conexión</Badge>;
  return <Badge tone="success">en línea</Badge>;
}
