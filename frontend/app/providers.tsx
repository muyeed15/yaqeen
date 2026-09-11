"use client";

import { SWRConfig } from "swr";
import { fetcher, SWR_CONFIG } from "@/utils/swr";

export function Providers({ children }: { children: React.ReactNode }): React.ReactElement {
  return <SWRConfig value={{ ...SWR_CONFIG, fetcher }}>{children}</SWRConfig>;
}
