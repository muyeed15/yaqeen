"use client";

import { useEffect } from "react";
import { logger } from "@/utils/logger";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}): React.ReactElement {
  useEffect(() => {
    logger.error("app:Error", "Unhandled root error", error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-6 text-center bg-sage">
      <h2 className="text-navy font-bold text-xl mb-2">Something went wrong</h2>
      <p className="text-navy-muted text-sm mb-6">
        {error.message ?? "An unexpected error occurred."}
      </p>
      <button
        type="button"
        onClick={reset}
        className="bg-teal text-white text-sm font-semibold px-5 py-2.5 rounded-xl"
      >
        Try again
      </button>
    </div>
  );
}
