"use client";

import { useAutoAnimate } from "@formkit/auto-animate/react";
import { X, Bell } from "lucide-react";

export type Toast = { id: number; message: string };

export function ToastStack({
  toasts,
  onDismiss,
}: {
  toasts: Toast[];
  onDismiss?: (id: number) => void;
}): React.ReactElement {
  const [parent] = useAutoAnimate();

  return (
    <div
      className="fixed top-4 right-4 z-50 flex flex-col gap-2 w-80 max-w-[calc(100vw-2rem)]"
      ref={parent}
    >
      {toasts.map((t) => (
        <div
          key={t.id}
          className="relative bg-white text-navy px-4 py-3.5 border border-sage-mid rounded-2xl shadow-lg shadow-navy/5 animate-scale-in"
        >
          <div className="flex items-start gap-3">
            <div className="h-8 w-8 bg-teal/10 rounded-xl flex items-center justify-center shrink-0">
              <Bell className="h-4 w-4 text-teal" />
            </div>
            <span className="block text-sm leading-snug pt-0.5 flex-1">{t.message}</span>
            {onDismiss && (
              <button
                type="button"
                onClick={() => onDismiss(t.id)}
                aria-label="Dismiss notification"
                className="shrink-0 text-navy-muted hover:text-navy active:scale-90 transition-all duration-150 mt-0.5"
              >
                <X className="h-4 w-4" aria-hidden="true" />
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
