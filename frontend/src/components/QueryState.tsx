import { AlertTriangle, Loader2, SearchX } from "lucide-react";
import { Card, CardContent } from "./ui/card";
import { ApiError } from "../services/apiClient";

/**
 * Estados de consulta explicitos. Existe para que ninguna pantalla caiga en el
 * patron de "no hay datos -> muestro algo inventado": si el backend no
 * responde o no encuentra nada, se dice.
 */

export function LoadingState({ label = "Consultando el registro" }: { label?: string }) {
  return (
    <Card>
      <CardContent className="flex items-center justify-center gap-3 px-6 py-16 text-sm text-muted">
        <Loader2 className="h-4 w-4 animate-spin text-accent" />
        {label}
      </CardContent>
    </Card>
  );
}

export function EmptyState({ title, copy }: { title: string; copy: string }) {
  return (
    <Card>
      <CardContent className="flex flex-col items-center px-6 py-16 text-center">
        <div className="grid h-12 w-12 place-items-center rounded-lg border border-border bg-[#181C21] text-[#66707B]">
          <SearchX className="h-5 w-5" />
        </div>
        <h3 className="mt-5 font-semibold">{title}</h3>
        <p className="mt-2 max-w-md text-sm leading-relaxed text-muted">{copy}</p>
      </CardContent>
    </Card>
  );
}

export function ErrorState({ error }: { error: unknown }) {
  const isApiError = error instanceof ApiError;
  const message = error instanceof Error ? error.message : "Error desconocido.";

  return (
    <Card className="border-danger/40">
      <CardContent className="flex flex-col items-center px-6 py-16 text-center">
        <div className="grid h-12 w-12 place-items-center rounded-lg border border-danger/40 bg-danger/10 text-danger">
          <AlertTriangle className="h-5 w-5" />
        </div>
        <h3 className="mt-5 font-semibold">No se pudo completar la consulta</h3>
        <p className="mt-2 max-w-md text-sm leading-relaxed text-muted">{message}</p>
        {isApiError && error.status > 0 && (
          <div className="mt-4 rounded-md border border-border bg-[#111418] px-3 py-1.5 font-mono text-[11px] text-[#66707B]">
            HTTP {error.status}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
