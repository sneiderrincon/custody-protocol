import * as React from "react";
import { cn } from "../../lib/utils";

export const Select = React.forwardRef<HTMLSelectElement, React.SelectHTMLAttributes<HTMLSelectElement>>(
  ({ className, ...props }, ref) => (
    <select
      ref={ref}
      className={cn(
        "h-10 w-full rounded-md border border-border bg-[#111418] px-3 text-sm text-white outline-none transition-colors focus:border-accent focus:outline focus:outline-2 focus:outline-offset-0 focus:outline-[rgba(232,163,61,0.34)]",
        className,
      )}
      {...props}
    />
  ),
);
Select.displayName = "Select";
