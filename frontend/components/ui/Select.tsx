import { SelectHTMLAttributes, forwardRef } from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/utils/helpers";

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, hint, className, id, children, ...props }, ref) => {
    const selectId = id ?? label?.toLowerCase().replace(/\s+/g, "-");
    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label
            htmlFor={selectId}
            className="text-[11px] font-semibold uppercase tracking-widest text-navy-muted select-none"
          >
            {label}
          </label>
        )}
        <div className="relative">
          <select
            ref={ref}
            id={selectId}
            className={cn(
              "w-full appearance-none border bg-white px-3.5 py-3 pr-10 text-sm text-navy rounded-xl outline-none transition-all duration-150",
              "hover:border-navy-muted/40",
              "focus:border-teal focus:ring-2 focus:ring-teal/10",
              "disabled:bg-sage disabled:text-navy-muted disabled:cursor-not-allowed",
              error
                ? "border-red-400 focus:border-red-500 focus:ring-red-500/10"
                : "border-sage-mid",
              className,
            )}
            {...props}
          >
            {children}
          </select>
          <ChevronDown
            className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-navy-muted"
            aria-hidden="true"
          />
        </div>
        {error && <p className="text-xs text-red-500 mt-0.5">{error}</p>}
        {hint && !error && <p className="text-xs text-navy-muted mt-0.5">{hint}</p>}
      </div>
    );
  },
);
Select.displayName = "Select";
