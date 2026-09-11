import Link from "next/link";
import { getMudarabahPlans } from "@/utils/api";
import { formatAmount, formatDuration } from "@/utils/helpers";
import { Vault } from "lucide-react";
import { PageHeader } from "@/components/ui/PageHeader";
import { StartSavingForm } from "./StartSavingForm";

export const dynamic = "force-dynamic";

export default async function SavingsPage() {
  const plans = await getMudarabahPlans();

  return (
    <div>
      <PageHeader title="Mudarabah Plans" subtitle="Savings" showBack backHref="/dashboard" />

      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-navy font-semibold">Available Plans</h2>
          <Link href="/savings/accounts" className="text-navy text-sm font-medium">
            My Accounts
          </Link>
        </div>

        {plans.length === 0 ? (
          <div className="bg-white border border-sage-mid px-6 py-10 text-center rounded-xl">
            <Vault className="h-8 w-8 text-sage-mid mb-3" />
            <p className="text-navy-muted text-sm">No savings plans available.</p>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2">
            {plans.map((plan) => (
              <div
                key={plan.id}
                className="bg-white border border-sage-mid rounded-xl overflow-hidden"
              >
                <div className="p-5">
                  <h3 className="text-navy font-bold text-base">{plan.name}</h3>
                  <p className="text-navy-muted text-sm mt-1">
                    {formatDuration(plan.duration_months)} &middot;{" "}
                    {formatAmount(plan.monthly_amount)}/mo
                  </p>
                  <p className="text-navy text-xs mt-1">Profit ratio: {plan.profit_ratio}%</p>
                </div>
                <div className="border-t border-sage-mid px-5 py-3">
                  <StartSavingForm planId={plan.id} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
