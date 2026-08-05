import * as React from "react";
import { cn } from "../../lib/utils";

export const Textarea = React.forwardRef<HTMLTextAreaElement, React.TextareaHTMLAttributes<HTMLTextAreaElement>>(
  ({ className, ...props }, ref) => (
    <textarea
      ref={ref}
      className={cn(
        "min-h-24 w-full resize-y rounded-md border border-border bg-[#111418] px-3 py-2 text-sm text-white outline-none transition-colors placeholder:text-[#66707B] focus:border-accent focus:outline focus:outline-2 focus:outline-offset-0 focus:outline-[rgba(232,163,61,0.34)]",
        className,
      )}
      {...props}
    />
  ),
);
Textarea.displayName = "Textarea";
