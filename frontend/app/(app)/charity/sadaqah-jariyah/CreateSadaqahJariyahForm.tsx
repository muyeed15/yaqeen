"use client";

import { useActionState } from "react";
import useSWR from "swr";
import { createSadaqahJariyahAction } from "@/app/actions";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Button } from "@/components/ui/Button";
import { formatAmount } from "@/utils/helpers";
import type { Foundation, FoundationCategory } from "@/types";

export function CreateSadaqahJariyahForm({ foundations }: { foundations: Foundation[] }) {
  const [state, action, pending] = useActionState(createSadaqahJariyahAction, null);
  const { data: causeData } = useSWR<FoundationCategory[]>("/api/foundation-causes");
  const causes = causeData ?? [];

  return (
    <div className="bg-white border border-sage-mid p-5 rounded-xl">
      <h2 className="text-navy font-semibold text-sm mb-4">Create Recurring Donation</h2>
      {state?.success && (
        <div className="mb-4 bg-teal/10 border border-teal/20 px-4 py-3 text-sm text-navy">
          Recurring donation of {formatAmount(state.amount)} created.
        </div>
      )}
      {state?.error && (
        <div className="mb-4 border-l-4 border-red-500 bg-red-50 px-4 py-3 text-sm text-red-700">
          {state.error}
        </div>
      )}
      <form action={action} className="space-y-4">
        <Select name="recipient_id" label="Foundation" required>
          <option value="">Select a foundation</option>
          {foundations.map((f) => (
            <option key={f.id} value={f.user_id}>
              {f.organization_name} &mdash; {f.cause_label}
            </option>
          ))}
        </Select>
        <Input
          label="Monthly Amount (৳)"
          name="amount"
          type="number"
          step="0.01"
          min="1"
          required
          placeholder="e.g. 1000"
        />
        <Select name="cause" label="Cause (Optional)">
          <option value="">No specific cause</option>
          {causes.map((c) => (
            <option key={c.key} value={c.key}>
              {c.label}
            </option>
          ))}
        </Select>
        <Button type="submit" variant="primary" loading={pending} className="w-full">
          {pending ? "Creating..." : "Create Recurring Donation"}
        </Button>
      </form>
    </div>
  );
}
