import { Loader2 } from "lucide-react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useSession } from "../auth/SessionContext";

/**
 * Guard de navegacion, no control de seguridad: solo evita que la UI se
 * renderice sin sesion. La proteccion real de los datos la aplica FastAPI en
 * cada peticion (arquitectura, seccion 3.1).
 */
export function RequireSession() {
  const { session, isRestoring } = useSession();
  const location = useLocation();

  if (isRestoring) {
    return (
      <div className="grid min-h-screen place-items-center">
        <Loader2 className="h-5 w-5 animate-spin text-accent" />
        <span className="sr-only">Restaurando sesión</span>
      </div>
    );
  }

  if (!session) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <Outlet />;
}
