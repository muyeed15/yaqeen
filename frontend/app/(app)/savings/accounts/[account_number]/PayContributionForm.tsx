"use client";

import { useActionState } from "react";
import { payContributionAction } from "@/app/actions";
import { Button } from "@/components/ui/Button";

export function PayContributionForm({
  accountNumber,
  monthlyAmount,
}: {
  accountNumber: string;
  monthlyAmount: string;
}) {
  const [state, action, pending] = useActionState(payContributionAction, null);

  return (
    <form action={action} className="bg-white border border-sage-mid p-4 mb-4 rounded-xl">
      <h3 className="text-navy font-semibold text-sm mb-2">Pay Next Contribution</h3>
      {state?.error && (
        <div className="mb-3 border-l-4 border-red-500 bg-red-50 px-3 py-2 text-sm text-red-700">
          {state.error}
        </div>
      )}
      <input type="hidden" name="account_number" value={accountNumber} />
      <div className="flex items-center gap-3">
        <input
          type="number"
          name="amount"
          defaultValue={monthlyAmount}
          step="0.01"
          min="0.01"
          required
          className="flex-1 border border-sage-mid px-3 py-2 text-sm text-navy focus:outline-none focus:border-teal rounded-lg"
        />
        <Button type="submit" variant="primary" size="sm" loading={pending}>
          {pending ? "Paying..." : "Pay"}
        </Button>
      </div>
    </form>
  );
}
