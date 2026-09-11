"use client";

import { useActionState } from "react";
import { calculateZakatAction } from "@/app/actions";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { formatAmount } from "@/utils/helpers";

export function CalculateZakatForm() {
  const [state, action, pending] = useActionState(calculateZakatAction, null);

  return (
    <div className="bg-white border border-sage-mid p-5 rounded-xl">
      <h2 className="text-navy font-semibold text-sm mb-4">Calculate Your Zakat</h2>
      <form action={action} className="space-y-4">
        <Input
          label="Total Wealth (৳)"
          name="total_wealth"
          type="number"
          step="0.01"
          min="0"
          required
          placeholder="e.g. 500000"
        />
        <Input
          label="Nisab Threshold (৳)"
          name="nisab_threshold"
          type="number"
          step="0.01"
          min="0"
          defaultValue="85000"
          placeholder="85000"
        />
        <Button type="submit" variant="primary" loading={pending}>
          {pending ? "Calculating..." : "Calculate"}
        </Button>
      </form>

      {state && !state.error && state.zakat_due !== undefined && (
        <div
          className={`mt-5 p-4 ${state.is_eligible ? "bg-teal/10 border border-teal/20 rounded-lg" : "bg-sage border border-sage-mid rounded-lg"}`}
        >
          <p className="text-sm font-semibold text-navy">
            {state.is_eligible ? "Zakat is Due" : "No Zakat Due"}
          </p>
          <p className="text-lg font-bold text-navy mt-1">{formatAmount(state.zakat_due)}</p>
          {state.is_eligible && (
            <a
              href="/charity/zakat/pay"
              className="inline-block mt-3 bg-teal text-white text-sm font-semibold px-4 py-2 rounded-lg"
            >
              Pay Zakat Now
            </a>
          )}
        </div>
      )}
    </div>
  );
}
