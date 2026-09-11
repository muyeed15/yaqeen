import { getZakatHistory } from "@/utils/api";
import { formatAmount, formatDate } from "@/utils/helpers";
import { PageHeader } from "@/components/ui/PageHeader";

export const dynamic = "force-dynamic";

export default async function ZakatHistoryPage() {
  const payments = await getZakatHistory().catch(() => []);
  const paymentList = Array.isArray(payments) ? payments : [];

  return (
    <div>
      <PageHeader title="Zakat History" subtitle="Charity" showBack backHref="/charity" />
      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl">
        <div className="bg-white border border-sage-mid divide-y divide-sage-mid rounded-xl">
          {paymentList.length === 0 ? (
            <div className="px-5 py-8 text-center text-navy-muted text-sm">
              No zakat payments yet.
            </div>
          ) : (
            paymentList.map((p) => (
              <div key={p.id} className="flex items-center justify-between px-5 py-3">
                <div>
                  <span className="text-navy font-medium text-sm">{formatAmount(p.amount)}</span>
                  {p.recipient_name && (
                    <p className="text-xs text-navy-muted">To: {p.recipient_name}</p>
                  )}
                </div>
                <span className="text-xs text-navy-muted">{formatDate(p.paid_at)}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
