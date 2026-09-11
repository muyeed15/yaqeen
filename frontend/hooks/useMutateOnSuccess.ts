"use client";

import { useEffect, useRef } from "react";
import { useSWRConfig } from "swr";

const API_KEY_FILTER = (key: unknown): boolean =>
  typeof key === "string" && key.startsWith("/api/");

/**
 * Revalidates every cached `/api/*` SWR key once when `success` becomes truthy.
 *
 * Client pages that read data with SWR are not affected by the server-side
 * `revalidatePath` calls in Server Actions, so they call this hook after a
 * successful mutation to refresh the list/history shown on the page.
 */
export function useMutateOnSuccess(success: boolean): void {
  const { mutate } = useSWRConfig();
  const wasSuccess = useRef(false);

  useEffect(() => {
    if (success && !wasSuccess.current) {
      void mutate(API_KEY_FILTER);
    }
    wasSuccess.current = success;
  }, [success, mutate]);
}
