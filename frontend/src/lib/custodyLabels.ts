import type { CustodyEventType } from "../types/custody";

/**
 * Presentacion de los tipos de evento. Las claves son exactamente los valores
 * que emite el backend; el texto es solo para lectura humana.
 */
const EVENT_LABELS: Record<CustodyEventType, string> = {
  Fabricado: "Fabricado",
  Enviado: "Enviado",
  Recibido: "Recibido",
  Despachado: "Despachado",
  UsadoImplantado: "Usado / implantado",
  Devuelto: "Devuelto",
  DadoDeBaja: "Dado de baja",
  EstadoInicialDeclarado: "Estado inicial declarado",
};

type Tone = "default" | "accent" | "success" | "danger";

const EVENT_TONES: Record<CustodyEventType, Tone> = {
  Fabricado: "default",
  Enviado: "accent",
  Recibido: "success",
  Despachado: "accent",
  UsadoImplantado: "success",
  Devuelto: "danger",
  DadoDeBaja: "danger",
  EstadoInicialDeclarado: "default",
};

export function eventLabel(eventType: CustodyEventType): string {
  return EVENT_LABELS[eventType] ?? eventType;
}

export function eventTone(eventType: CustodyEventType): Tone {
  return EVENT_TONES[eventType] ?? "default";
}

/** Fecha legible en la zona del navegador, con el ISO original en `title`. */
export function formatInstant(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;

  return new Intl.DateTimeFormat("es", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

/** UUID abreviado para tablas y listas, sin perder el valor completo. */
export function shortId(id: string): string {
  return id.length > 13 ? `${id.slice(0, 8)}…${id.slice(-4)}` : id;
}
