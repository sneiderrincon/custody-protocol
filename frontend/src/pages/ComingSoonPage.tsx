import { Construction } from "lucide-react";
import { Card, CardContent } from "../components/ui/card";

/**
 * Estado explicito para modulos sin backend (arquitectura, seccion 4):
 * la navegacion los muestra, pero nunca se inventan datos para llenarlos.
 */
export function ComingSoonPage({
  title,
  reason,
  missingEndpoint,
}: {
  title: string;
  reason: string;
  missingEndpoint?: string;
}) {
  return (
    <Card className="mt-6">
      <CardContent className="flex flex-col items-center px-6 py-16 text-center">
        <div className="grid h-12 w-12 place-items-center rounded-lg border border-border bg-[#181C21] text-accent">
          <Construction className="h-5 w-5" />
        </div>

        <h2 className="mt-5 text-lg font-semibold">{title}</h2>
        <p className="mt-2 max-w-md text-sm leading-relaxed text-muted">{reason}</p>

        {missingEndpoint && (
          <div className="mt-6 rounded-md border border-border bg-[#111418] px-3 py-2 font-mono text-[11px] text-[#66707B]">
            requiere: {missingEndpoint}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
