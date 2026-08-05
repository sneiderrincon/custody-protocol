/**
 * Cliente HTTP contra FastAPI.
 *
 * Nota de arquitectura: mientras no exista el BFF, la SPA habla directo con
 * FastAPI a traves del proxy de Vite. Cuando el BFF exista, solo cambia
 * `BASE_URL` a `/bff` y desaparece `authHeaders()` -- el JWT deja de vivir en
 * el navegador y pasa a resolverse server-side desde la cookie de sesion
 * (arquitectura, seccion 2.2).
 */

const BASE_URL = "";

/**
 * ADVERTENCIA: un JWT embebido en el bundle es visible para cualquiera que
 * abra el navegador. Es aceptable solo para demos locales contra datos de
 * prueba, y NUNCA debe desplegarse en un entorno accesible publicamente.
 * Generar con `python generar_token.py`.
 */
const DEMO_JWT = import.meta.env.VITE_DEMO_JWT;

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }

  /** El recurso no existe: los llamadores suelen querer un estado vacio, no un error. */
  get isNotFound(): boolean {
    return this.status === 404;
  }
}

/** Extrae el `detail` de FastAPI, que puede ser texto o lista de errores de validacion. */
function readDetail(body: unknown, fallback: string): string {
  if (typeof body !== "object" || body === null || !("detail" in body)) {
    return fallback;
  }

  const detail = (body as { detail: unknown }).detail;
  if (typeof detail === "string") return detail;

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) =>
        typeof item === "object" && item !== null && "msg" in item
          ? String((item as { msg: unknown }).msg)
          : null,
      )
      .filter((msg): msg is string => msg !== null);

    if (messages.length > 0) return messages.join(". ");
  }

  return fallback;
}

function authHeaders(): Record<string, string> {
  return DEMO_JWT ? { Authorization: `Bearer ${DEMO_JWT}` } : {};
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${BASE_URL}${path}`, {
      ...init,
      headers: {
        Accept: "application/json",
        ...(init?.body ? { "Content-Type": "application/json" } : {}),
        ...authHeaders(),
        ...init?.headers,
      },
    });
  } catch (cause) {
    // fetch solo rechaza por fallo de red; un 4xx/5xx llega como respuesta.
    throw new ApiError(0, "No se pudo contactar al servidor. ¿Está corriendo la API?");
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(response.status, readDetail(body, `Error ${response.status}`));
  }

  return (await response.json()) as T;
}

export const apiClient = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }),
};

/** `true` si hay credencial para operaciones de escritura. */
export const canWrite = Boolean(DEMO_JWT);
