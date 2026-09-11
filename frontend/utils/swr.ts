import type { SWRConfiguration } from "swr";
import { logger } from "./logger";

export const SWR_CONFIG: SWRConfiguration = {
  revalidateOnFocus: true,
  revalidateOnReconnect: true,
};

const toastDuration = process.env.NEXT_PUBLIC_TOAST_DURATION_MS;
if (!toastDuration) throw new Error("NEXT_PUBLIC_TOAST_DURATION_MS must be set in frontend/.env");
export const TOAST_DURATION_MS = parseInt(toastDuration);

export async function fetcher<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (res.status === 401 && typeof window !== "undefined") {
    logger.warn("swr:fetcher", "Unauthorized; redirecting to login", { url });
    window.location.href = "/login";
    throw new Error("Unauthorized");
  }
  if (!res.ok) {
    logger.error("swr:fetcher", `Request failed`, { url, status: res.status });
    throw new Error(`Request failed: ${res.status}`);
  }
  return res.json();
}
