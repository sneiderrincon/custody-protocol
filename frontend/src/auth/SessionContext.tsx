import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { DemoSessionProvider } from "./DemoSessionProvider";
import type { PermissionId, Session, SessionProvider } from "./types";

// Punto unico de cambio cuando exista el BFF:
// const sessionProvider: SessionProvider = new BffSessionProvider();
const sessionProvider: SessionProvider = new DemoSessionProvider();

interface SessionContextValue {
  session: Session | null;
  /** `true` mientras se intenta recuperar la sesion al cargar la pagina. */
  isRestoring: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const SessionContext = createContext<SessionContextValue | null>(null);

export function SessionProviderComponent({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [isRestoring, setIsRestoring] = useState(true);

  useEffect(() => {
    let cancelled = false;

    sessionProvider
      .restore()
      .then((restored) => {
        if (!cancelled) setSession(restored);
      })
      .finally(() => {
        if (!cancelled) setIsRestoring(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setSession(await sessionProvider.login(email, password));
  }, []);

  const logout = useCallback(async () => {
    await sessionProvider.logout();
    setSession(null);
  }, []);

  const value = useMemo(
    () => ({ session, isRestoring, login, logout }),
    [session, isRestoring, login, logout],
  );

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession(): SessionContextValue {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error("useSession debe usarse dentro de <SessionProviderComponent>");
  }
  return context;
}

/**
 * Permisos para ocultar o deshabilitar UI. Nunca es seguridad: la autorizacion
 * real la aplica FastAPI (arquitectura, seccion 3.1).
 */
export function useCan(permission: PermissionId): boolean {
  const { session } = useSession();
  return session?.permissions.includes(permission) ?? false;
}
