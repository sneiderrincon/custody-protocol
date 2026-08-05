import { useState, type FormEvent } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { FileClock, Loader2, LockKeyhole, ScanSearch, ShieldCheck } from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { demoCredentials } from "../auth/DemoSessionProvider";
import { useSession } from "../auth/SessionContext";

const valueProps = [
  {
    icon: FileClock,
    title: "Cadena de custodia inmutable",
    copy: "Cada aserción es append-only y queda sellada con SHA-256. Nada se edita, nada se borra.",
  },
  {
    icon: ScanSearch,
    title: "Trazabilidad forense por UDI",
    copy: "Reconstruye el recorrido completo de un dispositivo médico desde fábrica hasta paciente.",
  },
  {
    icon: ShieldCheck,
    title: "Autorización fail-closed",
    copy: "Sin permiso explícito no hay operación. El backend rechaza por defecto, no por excepción.",
  },
];

export function LoginPage() {
  const { session, login } = useSession();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const redirectTo = (location.state as { from?: string } | null)?.from ?? "/app/buscar";

  if (session) {
    return <Navigate to={redirectTo} replace />;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await login(email, password);
      navigate(redirectTo, { replace: true });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "No se pudo iniciar sesión.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[minmax(0,1fr)_520px]">
      <section className="relative hidden flex-col justify-between overflow-hidden border-r border-border bg-[#0D1013] p-12 lg:flex">
        <div
          aria-hidden
          className="pointer-events-none absolute -right-32 -top-32 h-96 w-96 rounded-full bg-accent/10 blur-3xl"
        />

        <div className="flex items-center gap-3">
          <div className="grid h-9 w-9 place-items-center rounded-lg border border-border bg-panel text-accent">
            <ShieldCheck className="h-4 w-4" />
          </div>
          <div>
            <div className="font-semibold">Kernel</div>
            <div className="font-mono text-[11px] text-[#66707B]">medical trace protocol</div>
          </div>
        </div>

        <div className="relative max-w-lg">
          <h1 className="text-balance text-4xl font-semibold leading-tight">
            La cadena de custodia de cada dispositivo médico, verificable línea por línea.
          </h1>
          <p className="mt-4 text-balance text-muted">
            Fabricantes, distribuidores, hospitales y auditores regulatorios operando sobre un
            mismo registro append-only.
          </p>

          <ul className="mt-10 space-y-6">
            {valueProps.map(({ icon: Icon, title, copy }) => (
              <li key={title} className="flex gap-4">
                <div className="mt-0.5 grid h-9 w-9 shrink-0 place-items-center rounded-lg border border-border bg-panel text-accent">
                  <Icon className="h-4 w-4" />
                </div>
                <div>
                  <div className="font-semibold">{title}</div>
                  <p className="mt-1 text-sm text-muted">{copy}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>

        <div className="relative font-mono text-[11px] text-[#66707B]">
          INVIMA · FDA · MDR — trazabilidad regulatoria
        </div>
      </section>

      <section className="flex min-h-screen flex-col justify-center px-6 py-12 sm:px-12">
        <div className="mx-auto w-full max-w-sm">
          <div className="mb-8 flex items-center gap-3 lg:hidden">
            <div className="grid h-9 w-9 place-items-center rounded-lg border border-border bg-panel text-accent">
              <ShieldCheck className="h-4 w-4" />
            </div>
            <div className="font-semibold">Kernel</div>
          </div>

          <h2 className="text-2xl font-semibold">Iniciar sesión</h2>
          <p className="mt-2 text-sm text-muted">
            Accede a la consola de trazabilidad de tu organización.
          </p>

          <form className="mt-8 space-y-5" onSubmit={handleSubmit} noValidate>
            <div className="space-y-2">
              <Label htmlFor="email">Correo corporativo</Label>
              <Input
                id="email"
                type="email"
                autoComplete="username"
                placeholder="nombre@organizacion.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Contraseña</Label>
              <Input
                id="password"
                type="password"
                autoComplete="current-password"
                placeholder="••••••••"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />
            </div>

            {error && (
              <p
                role="alert"
                className="rounded-md border border-danger/40 bg-danger/10 px-3 py-2 text-sm text-danger"
              >
                {error}
              </p>
            )}

            <Button type="submit" variant="primary" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Verificando
                </>
              ) : (
                <>
                  <LockKeyhole className="h-4 w-4" />
                  Entrar
                </>
              )}
            </Button>
          </form>

          {/*
            Aviso deliberadamente visible: esta pantalla es una fachada de
            demostración, no autenticación. Debe desaparecer junto con
            DemoSessionProvider cuando el BFF exista.
          */}
          <div className="mt-8 rounded-lg border border-border bg-panel p-4">
            <div className="mb-2 font-mono text-[10px] uppercase tracking-[0.08em] text-accent">
              Entorno de demostración
            </div>
            <p className="text-xs leading-relaxed text-muted">
              Aún no existe el servicio de autenticación (BFF). Esta pantalla valida credenciales
              en el navegador y no protege ningún dato.
            </p>
            <div className="mt-3 space-y-1 font-mono text-[11px] text-[#66707B]">
              <div>usuario: {demoCredentials.email}</div>
              <div>clave: {demoCredentials.password}</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
