"use client";

import { useEffect } from "react";
import { AlertTriangle } from "lucide-react";
import { logger } from "@/utils/logger";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}): React.ReactElement {
  useEffect(() => {
    logger.error("app:(app):Error", "Unhandled layout error", error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] px-6 text-center">
      <AlertTriangle className="h-10 w-10 text-navy-muted mb-4" aria-hidden="true" />
      <h2 className="text-navy font-bold text-lg mb-1">Something went wrong</h2>
      <p className="text-navy-muted text-sm mb-6 max-w-sm">
        {error.message ?? "An unexpected error occurred. Please try again."}
      </p>
      <button
        type="button"
        onClick={reset}
        className="bg-teal text-white text-sm font-semibold px-5 py-2.5 active:opacity-80 transition-opacity"
      >
        Try again
      </button>
    </div>
  );
}
