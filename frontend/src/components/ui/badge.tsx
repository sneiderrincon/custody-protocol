import * as React from "react";
import { cn } from "../../lib/utils";

type BadgeTone = "default" | "accent" | "success" | "danger";

const tones: Record<BadgeTone, string> = {
  default: "border-border bg-[#111418] text-muted",
  accent: "border-[#514028] bg-[#2C2419] text-accent",
  success: "border-[#254333] bg-[#18251D] text-success",
  danger: "border-[#55302B] bg-[#2A1B19] text-danger",
};

export function Badge({
  className,
  tone = "default",
  ...props
}: React.HTMLAttributes<HTMLSpanElement> & { tone?: BadgeTone }) {
  return (
    <span
      className={cn(
        "inline-flex min-h-6 items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs",
        tones[tone],
        className,
      )}
      {...props}
    />
  );
}
