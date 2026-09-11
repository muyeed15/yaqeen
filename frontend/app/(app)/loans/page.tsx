import Link from "next/link";
import { getQardHasanProducts } from "@/utils/api";
import { formatAmount } from "@/utils/helpers";
import { HandCoins } from "lucide-react";
import { PageHeader } from "@/components/ui/PageHeader";

export const dynamic = "force-dynamic";

export default async function LoansPage() {
  const products = await getQardHasanProducts();

  return (
    <div>
      <PageHeader
        title="Qard Hasan Plans"
        subtitle="Interest-Free Loan"
        showBack
        backHref="/dashboard"
      />

      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-navy font-semibold">Available Plans</h2>
          <Link href="/loans/my" className="text-navy text-sm font-medium">
            My Loans
          </Link>
        </div>

        {products.length === 0 ? (
          <div className="bg-white border border-sage-mid px-6 py-10 text-center rounded-xl">
            <HandCoins className="h-8 w-8 text-sage-mid mb-3 mx-auto" />
            <p className="text-navy-muted text-sm">No loan plans available.</p>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2">
            {products.map((p) => (
              <div
                key={p.id}
                className="bg-white border border-sage-mid rounded-xl overflow-hidden"
              >
                <div className="p-5">
                  <h3 className="text-navy font-bold text-base">{p.name}</h3>
                  <p className="text-navy-muted text-sm mt-1">
                    Up to {formatAmount(p.max_amount)} &middot; {p.tenure_days} days
                  </p>
                  <p className="text-navy text-xs mt-1">
                    Service fee: {formatAmount(p.service_fee)}
                  </p>
                  <p className="text-teal text-xs mt-1 font-medium">0% Riba (Interest-free)</p>
                </div>
                <div className="border-t border-sage-mid px-5 py-3">
                  <Link
                    href={`/loans/apply/${p.id}`}
                    className="bg-teal text-white text-sm font-semibold px-4 py-2 w-full rounded-lg block text-center"
                  >
                    Apply
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
