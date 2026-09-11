import Link from "next/link";
import { getSadaqahHistory } from "@/utils/api";
import { formatAmount, formatDate } from "@/utils/helpers";
import { PageHeader } from "@/components/ui/PageHeader";

export const dynamic = "force-dynamic";

export default async function SadaqahHistoryPage() {
  const sadaqahList = await getSadaqahHistory().catch(() => []);
  const list = Array.isArray(sadaqahList) ? sadaqahList : [];

  return (
    <div>
      <PageHeader title="Sadaqah History" subtitle="Charity" showBack backHref="/charity/sadaqah" />
      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl">
        <div className="flex items-center justify-between mb-3">
          <p className="text-[11px] font-semibold uppercase tracking-widest text-navy-muted">
            My Donations
          </p>
          <Link href="/charity/sadaqah" className="text-navy text-sm font-medium">
            Give
          </Link>
        </div>

        <div className="bg-white border border-sage-mid divide-y divide-sage-mid rounded-xl">
          {list.length === 0 ? (
            <div className="px-5 py-8 text-center text-navy-muted text-sm">
              No sadaqah donations yet.
            </div>
          ) : (
            list.map((d) => (
              <div key={d.id} className="flex items-center justify-between px-5 py-3">
                <div>
                  <span className="text-navy font-medium text-sm">{formatAmount(d.amount)}</span>
                  {d.cause_label && <p className="text-xs text-navy-muted">{d.cause_label}</p>}
                  {d.recipient_name && (
                    <p className="text-xs text-navy-muted">To: {d.recipient_name}</p>
                  )}
                </div>
                <span className="text-xs text-navy-muted">{formatDate(d.given_at)}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
