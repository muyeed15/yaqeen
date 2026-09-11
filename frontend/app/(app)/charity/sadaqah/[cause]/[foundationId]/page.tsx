"use client";

import { useActionState } from "react";
import { useParams, useRouter } from "next/navigation";
import useSWR from "swr";
import { ArrowLeft, Info } from "lucide-react";
import { giveSadaqahAction } from "@/app/actions";
import type { Foundation, FoundationCategory } from "@/types";
import { EntityLogo } from "@/components/ui/EntityLogo";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Button } from "@/components/ui/Button";
import { PageTransition } from "@/components/ui/PageTransition";

const initialState = null;

export default function GiveSadaqahFoundationPage() {
  const { cause, foundationId } = useParams<{
    cause: string;
    foundationId: string;
  }>();
  const router = useRouter();
  const [state, formAction, pending] = useActionState(giveSadaqahAction, initialState);

  const { data } = useSWR<Foundation[]>(`/api/foundations?cause=${encodeURIComponent(cause)}`);
  const { data: causeData } = useSWR<FoundationCategory[]>("/api/foundation-causes");
  const foundation = (data ?? []).find((f) => f.user_id === Number(foundationId)) ?? null;
  const causes = causeData ?? [];

  return (
    <PageTransition>
      <div className="bg-white px-4 h-16 flex items-center gap-3 border-b border-sage/80">
        <button
          type="button"
          onClick={() => router.push(`/charity/sadaqah/${cause}`)}
          aria-label="Go back"
          className="text-navy-muted hover:text-navy active:scale-90 transition-all duration-150"
        >
          <ArrowLeft className="h-5 w-5" aria-hidden="true" />
        </button>
        <div>
          <p className="text-[10px] text-navy-muted font-semibold uppercase tracking-widest leading-none">
            Give Sadaqah
          </p>
          <h1 className="text-navy font-bold text-lg leading-tight mt-0.5">
            {foundation?.organization_name ?? "Donate"}
          </h1>
        </div>
      </div>

      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl space-y-5">
        {state?.success && (
          <div className="bg-teal/10 border border-teal/30 rounded-xl px-4 py-3 text-sm font-medium text-teal">
            Donated ৳{state.amount} successfully. JazakAllah Khair.
          </div>
        )}

        {foundation && (
          <form
            action={formAction}
            className="bg-white border border-sage-mid rounded-2xl p-5 shadow-sm space-y-5"
          >
            <div className="flex gap-2 items-start">
              <Info className="h-4 w-4 mt-0.5 shrink-0 text-navy-muted" />
              <p className="text-xs leading-snug text-navy-muted">
                Your sadaqah is given instantly to the selected foundation.
              </p>
            </div>

            <div className="bg-sage/50 rounded-xl px-4 py-3 flex items-center gap-3">
              <EntityLogo logo={foundation.logo} name={foundation.organization_name} />
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-widest text-navy-muted">
                  Foundation
                </p>
                <p className="text-sm font-semibold text-navy">{foundation.organization_name}</p>
              </div>
            </div>

            <input type="hidden" name="recipient_id" value={foundation.user_id} />

            <Input
              name="amount"
              label="Amount (৳)"
              type="number"
              step="0.01"
              min="1"
              required
              placeholder="e.g. 500"
            />
            <Select
              id="cause"
              name="cause"
              label="Cause (Optional)"
              defaultValue={foundation.cause ?? ""}
            >
              <option value="">No specific cause</option>
              {causes.map((c) => (
                <option key={c.key} value={c.key}>
                  {c.label}
                </option>
              ))}
            </Select>
            <label className="flex items-center gap-2 text-sm text-navy">
              <input type="checkbox" name="is_anonymous" value="true" className="accent-teal" />
              Donate anonymously
            </label>

            {state?.error && (
              <div className="border-l-4 border-red-500 bg-red-50 px-4 py-3 text-sm text-red-700 rounded-r">
                {state.error}
              </div>
            )}

            <Button
              type="submit"
              loading={pending}
              className="w-full h-auto py-4 text-base rounded-xl"
            >
              {pending ? "Donating..." : "Donate"}
            </Button>
          </form>
        )}

        {state?.success && (
          <Button
            type="button"
            variant="secondary"
            onClick={() => router.push("/charity/sadaqah/history")}
            className="w-full"
          >
            View History
          </Button>
        )}
      </div>
    </PageTransition>
  );
}
