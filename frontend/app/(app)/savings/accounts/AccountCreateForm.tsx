"use client";

import { useActionState } from "react";
import { createMudarabahAccountAction } from "@/app/actions";
import { Button } from "@/components/ui/Button";
import { Select } from "@/components/ui/Select";
import { formatDuration } from "@/utils/helpers";
import type { MudarabahPlan } from "@/types";

export function AccountCreateForm({ plans }: { plans: MudarabahPlan[] }) {
  const [state, action, pending] = useActionState(createMudarabahAccountAction, null);

  return (
    <form action={action} className="bg-white border border-sage-mid p-5 rounded-xl">
      <h3 className="text-navy font-semibold text-sm mb-3">Open New Account</h3>
      {state?.error && (
        <div className="mb-3 border-l-4 border-red-500 bg-red-50 px-3 py-2 text-sm text-red-700">
          {state.error}
        </div>
      )}
      <Select name="plan_id" label="Plan" required className="mb-3">
        <option value="">Select a plan</option>
        {plans.map((p) => (
          <option key={p.id} value={p.id}>
            {p.name} &mdash; ৳{p.monthly_amount}/mo &middot; {formatDuration(p.duration_months)}
          </option>
        ))}
      </Select>
      <Button type="submit" variant="primary" size="md" loading={pending} className="w-full">
        {pending ? "Creating..." : "Open Account"}
      </Button>
    </form>
  );
}
