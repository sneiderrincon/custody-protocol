/**
 * Puerto de sesion (arquitectura, seccion 4: `domain/ports`).
 *
 * La UI depende solo de esta interfaz, nunca de como se obtiene la sesion.
 * Hoy la implementa `DemoSessionProvider` (fachada local, sin backend de auth);
 * cuando exista el BFF se implementa `BffSessionProvider` contra
 * `POST /bff/auth/login`, `GET /bff/auth/me` y `POST /bff/auth/logout`,
 * y se cambia una sola linea en `SessionContext.tsx`.
 */

/** Permisos con el vocabulario de la matriz unica (arquitectura, seccion 3.3). */
export type PermissionId =
  | "custody:dispatch:create"
  | "custody:history:read"
  | "catalog:device:register"
  | "catalog:device:read";

export interface Session {
  readonly email: string;
  readonly displayName: string;
  /** `actor_id` de FastAPI: el claim `sub` del JWT que el backend verifica. */
  readonly actorId: string;
  readonly organizationName: string;
  readonly permissions: readonly PermissionId[];
}

export class InvalidCredentialsError extends Error {
  constructor() {
    super("Correo o contrasena incorrectos.");
    this.name = "InvalidCredentialsError";
  }
}

export interface SessionProvider {
  login(email: string, password: string): Promise<Session>;
  logout(): Promise<void>;
  /** Recupera la sesion al recargar la pagina. `null` si no hay ninguna. */
  restore(): Promise<Session | null>;
}
