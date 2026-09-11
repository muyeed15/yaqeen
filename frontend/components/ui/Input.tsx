import { InputHTMLAttributes, forwardRef } from "react";
import { cn } from "@/utils/helpers";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, className, id, ...props }, ref) => {
    const inputId = id ?? label?.toLowerCase().replace(/\s+/g, "-");
    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label
            htmlFor={inputId}
            className="text-[11px] font-semibold uppercase tracking-widest text-navy-muted select-none"
          >
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={cn(
            "w-full border bg-white px-3.5 py-3 text-sm text-navy placeholder:text-navy-muted/60 rounded-xl outline-none transition-all duration-150",
            "hover:border-navy-muted/40",
            "focus:border-teal focus:ring-2 focus:ring-teal/10",
            "disabled:bg-sage disabled:text-navy-muted disabled:cursor-not-allowed",
            error ? "border-red-400 focus:border-red-500 focus:ring-red-500/10" : "border-sage-mid",
            className,
          )}
          {...props}
        />
        {error && <p className="text-xs text-red-500 mt-0.5">{error}</p>}
        {hint && !error && <p className="text-xs text-navy-muted mt-0.5">{hint}</p>}
      </div>
    );
  },
);
Input.displayName = "Input";
