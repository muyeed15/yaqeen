"use client";

import { useEffect } from "react";
import "./globals.css";
import { logger } from "@/utils/logger";

// `global-error` replaces the root layout when an error is thrown there, so it
// must render its own <html> and <body>. It is the only error boundary allowed
// to do so; `app/error.tsx` renders inside the root layout and must not.
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}): React.ReactElement {
  useEffect(() => {
    logger.error("app:GlobalError", "Unhandled global error", error);
  }, [error]);

  return (
    <html lang="en">
      <body className="flex flex-col items-center justify-center min-h-screen px-6 text-center bg-sage">
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
      </body>
    </html>
  );
}
