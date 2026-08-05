import { Badge } from "./ui/badge";

export function PageHeader({
  eyebrow,
  title,
  copy,
  badges,
}: {
  eyebrow: string;
  title: string;
  copy: string;
  badges: Array<{ label: string; tone?: "default" | "accent" | "success" | "danger" }>;
}) {
  return (
    <div className="flex flex-col gap-5 py-7 lg:flex-row lg:items-start lg:justify-between">
      <div>
        <div className="mb-2 font-mono text-[11px] uppercase tracking-[0.1em] text-accent">{eyebrow}</div>
        <h1 className="max-w-4xl text-balance text-3xl font-semibold tracking-normal text-white md:text-4xl">{title}</h1>
        <p className="mt-3 max-w-3xl text-sm leading-6 text-muted">{copy}</p>
      </div>
      <div className="flex flex-wrap gap-2 lg:justify-end">
        {badges.map((badge) => (
          <Badge key={badge.label} tone={badge.tone}>
            {badge.label}
          </Badge>
        ))}
      </div>
    </div>
  );
}
