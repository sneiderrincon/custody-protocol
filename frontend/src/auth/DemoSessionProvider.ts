import {
  InvalidCredentialsError,
  type PermissionId,
  type Session,
  type SessionProvider,
} from "./types";

/**
 * Fachada de sesion para demostraciones comerciales.
 *
 * ESTO NO ES AUTENTICACION. No valida nada contra un servidor, no emite tokens
 * y no protege ningun dato: cualquiera que abra las herramientas de desarrollo
 * puede saltarselo. Existe unicamente para que el recorrido de venta
 * (login -> modulos) se pueda mostrar antes de que exista el BFF.
 *
 * La autenticacion real vive en el BFF (arquitectura, seccion 2.1) y llega
 * implementando `SessionProvider` contra `/bff/auth/*`, sin tocar la UI.
 */

const STORAGE_KEY = "custody.demo.session";

const DEMO_EMAIL = import.meta.env.VITE_DEMO_EMAIL ?? "demo@custodyprotocol.io";
const DEMO_PASSWORD = import.meta.env.VITE_DEMO_PASSWORD ?? "demo";
const DEMO_ACTOR_ID =
  import.meta.env.VITE_DEMO_ACTOR_ID ?? "3fa85f64-5717-4562-b3fc-2c963f66afa6";

/**
 * Todos los permisos que la UI conoce hoy. Solo `catalog:device:register`
 * tiene respaldo real en FastAPI (`MANAGE_CATALOG`); el resto es UX
 * (arquitectura, seccion 3.1) y el backend lo permite a cualquier actor
 * autenticado.
 */
const DEMO_PERMISSIONS: readonly PermissionId[] = [
  "custody:dispatch:create",
  "custody:history:read",
  "catalog:device:register",
  "catalog:device:read",
];

const demoSession: Session = {
  email: DEMO_EMAIL,
  displayName: "Usuario de demostracion",
  actorId: DEMO_ACTOR_ID,
  organizationName: "Organizacion de demostracion",
  permissions: DEMO_PERMISSIONS,
};

function readStoredSession(): Session | null {
  const raw = window.sessionStorage.getItem(STORAGE_KEY);
  if (!raw) return null;

  try {
    return JSON.parse(raw) as Session;
  } catch {
    // Sesion corrupta: se descarta en vez de romper el arranque de la app.
    window.sessionStorage.removeItem(STORAGE_KEY);
    return null;
  }
}

export class DemoSessionProvider implements SessionProvider {
  async login(email: string, password: string): Promise<Session> {
    const matches =
      email.trim().toLowerCase() === DEMO_EMAIL.toLowerCase() &&
      password === DEMO_PASSWORD;

    if (!matches) {
      throw new InvalidCredentialsError();
    }

    const session: Session = { ...demoSession, email: email.trim() };
    window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(session));
    return session;
  }

  async logout(): Promise<void> {
    window.sessionStorage.removeItem(STORAGE_KEY);
  }

  async restore(): Promise<Session | null> {
    return readStoredSession();
  }
}

/** Credenciales que la pantalla de login muestra durante la demo. */
export const demoCredentials = {
  email: DEMO_EMAIL,
  password: DEMO_PASSWORD,
};
