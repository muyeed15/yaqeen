import { revalidatePath } from "next/cache";
import { cookies } from "next/headers";
import { API } from "@/utils/config";

export { API };

export async function token(): Promise<string | undefined> {
  return (await cookies()).get("access_token")?.value;
}

// Pages that reflect the wallet balance, unified transaction history, and
// notification feed. Server Actions must invalidate these so client-side
// navigation never serves a stale cache after a mutation.
const LEDGER_PATHS = ["/dashboard", "/transactions", "/notifications", "/profile"];

export function revalidateLedger(...extraPaths: string[]): void {
  for (const path of [...LEDGER_PATHS, ...extraPaths]) {
    revalidatePath(path);
  }
}
