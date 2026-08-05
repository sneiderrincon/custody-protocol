import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ChevronDown, Fingerprint, Hash, Paperclip } from "lucide-react";
import { Badge } from "../ui/badge";
import { Card } from "../ui/card";
import { eventLabel, eventTone, formatInstant, shortId } from "../../lib/custodyLabels";
import type { CommittedCustodyAssertion } from "../../types/custody";

/**
 * Linea de tiempo append-only. Muestra unicamente campos que el backend
 * devuelve de verdad: no hay nombre de actor ni ubicacion porque el modelo de
 * dominio no los tiene (`Provenance` solo expone `actor_id` y `adapter_id`).
 */
export function AssertionTimeline({
  assertions,
}: {
  assertions: CommittedCustodyAssertion[];
}) {
  const [openClaim, setOpenClaim] = useState<string | null>(null);

  return (
    <div className="relative pl-8">
      <div aria-hidden className="absolute bottom-3 left-[11px] top-3 w-px bg-border" />

      <ol className="space-y-4">
        {assertions.map((assertion, index) => {
          const isOpen = openClaim === assertion.claim_id;
          const attributes = assertion.payload?.attributes ?? [];
          const evidence = assertion.provenance.evidence ?? [];

          return (
            <motion.li
              key={assertion.claim_id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: Math.min(index * 0.04, 0.32), duration: 0.24 }}
              className="relative"
            >
              <span
                aria-hidden
                className="absolute -left-[29px] top-5 h-[9px] w-[9px] rounded-full border-2 border-background bg-accent"
              />

              <Card>
                <button
                  type="button"
                  onClick={() => setOpenClaim(isOpen ? null : assertion.claim_id)}
                  aria-expanded={isOpen}
                  className="flex w-full items-center justify-between gap-4 p-4 text-left transition-colors hover:bg-[#181C21]"
                >
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge tone={eventTone(assertion.event_type)}>
                        {eventLabel(assertion.event_type)}
                      </Badge>
                      <span
                        className="text-sm text-muted"
                        title={assertion.occurred_at}
                      >
                        {formatInstant(assertion.occurred_at)}
                      </span>
                    </div>
                    <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 font-mono text-[11px] text-[#66707B]">
                      <span title={assertion.provenance.actor_id}>
                        actor {shortId(assertion.provenance.actor_id)}
                      </span>
                      <span>adaptador {assertion.provenance.adapter_id}</span>
                      <span>v{assertion.stream_version}</span>
                    </div>
                  </div>

                  <ChevronDown
                    className={`h-4 w-4 shrink-0 text-[#66707B] transition-transform ${
                      isOpen ? "rotate-180" : ""
                    }`}
                  />
                </button>

                <AnimatePresence initial={false}>
                  {isOpen && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.18 }}
                      className="overflow-hidden"
                    >
                      <dl className="space-y-3 border-t border-[#1E232A] p-4 text-sm">
                        <Field icon={Fingerprint} label="claim_id">
                          <span className="break-all font-mono text-xs">
                            {assertion.claim_id}
                          </span>
                        </Field>

                        <Field icon={Hash} label="posición global">
                          <span className="font-mono text-xs">
                            {assertion.global_position.toLocaleString("es")}
                          </span>
                        </Field>

                        <Field icon={Fingerprint} label="declarado el">
                          <span
                            className="font-mono text-xs"
                            title={assertion.provenance.declared_at}
                          >
                            {formatInstant(assertion.provenance.declared_at)}
                          </span>
                        </Field>

                        {evidence.length > 0 && (
                          <Field icon={Paperclip} label="evidencia">
                            <ul className="space-y-2">
                              {evidence.map((item) => (
                                <li key={item.sha256}>
                                  <div className="break-all font-mono text-xs text-white">
                                    {item.uri}
                                  </div>
                                  <div className="break-all font-mono text-[10px] text-[#66707B]">
                                    sha256 {item.sha256}
                                  </div>
                                </li>
                              ))}
                            </ul>
                          </Field>
                        )}

                        {attributes.length > 0 && (
                          <Field icon={Paperclip} label="atributos del adaptador">
                            <ul className="space-y-1 font-mono text-xs">
                              {attributes.map((attribute) => (
                                <li key={attribute.key}>
                                  <span className="text-[#66707B]">{attribute.key}: </span>
                                  <span>{String(attribute.value)}</span>
                                </li>
                              ))}
                            </ul>
                          </Field>
                        )}
                      </dl>
                    </motion.div>
                  )}
                </AnimatePresence>
              </Card>
            </motion.li>
          );
        })}
      </ol>
    </div>
  );
}

function Field({
  icon: Icon,
  label,
  children,
}: {
  icon: typeof Hash;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex gap-3">
      <Icon className="mt-0.5 h-3.5 w-3.5 shrink-0 text-[#66707B]" />
      <div className="min-w-0 flex-1">
        <dt className="font-mono text-[10px] uppercase tracking-[0.08em] text-[#66707B]">
          {label}
        </dt>
        <dd className="mt-1 min-w-0">{children}</dd>
      </div>
    </div>
  );
}
