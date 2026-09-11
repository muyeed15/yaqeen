import { getMudarabahAccount, getMudarabahContributions } from "@/utils/api";
import { formatAmount, formatDate } from "@/utils/helpers";
import { Badge } from "@/components/ui/Badge";
import { PageHeader } from "@/components/ui/PageHeader";
import { PayContributionForm } from "./PayContributionForm";

export const dynamic = "force-dynamic";

export default async function SavingsAccountDetailPage({
  params,
}: {
  params: Promise<{ account_number: string }>;
}) {
  const { account_number } = await params;
  const [account, contributions] = await Promise.all([
    getMudarabahAccount(account_number),
    getMudarabahContributions(account_number).catch(() => []),
  ]);

  const contributionList = Array.isArray(contributions) ? contributions : [];
  const paidCount = contributionList.filter((c) => c.status === "paid").length;
  const totalInstallments = account.plan_details?.duration_months ?? 0;
  const nextNumber = paidCount + 1;
  const isComplete = nextNumber > totalInstallments;

  return (
    <div>
      <PageHeader
        title={account.account_number}
        subtitle="Account"
        showBack
        backHref="/savings/accounts"
      />
      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl">
        <div className="bg-white border border-sage-mid p-5 mb-6 rounded-xl">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-navy font-semibold">{account.plan_details?.name}</h2>
            <Badge
              variant={
                account.status === "active"
                  ? "success"
                  : account.status === "matured"
                    ? "warning"
                    : "neutral"
              }
            >
              {account.status}
            </Badge>
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-navy-muted">Deposited</span>
              <p className="text-navy font-semibold">{formatAmount(account.total_deposited)}</p>
            </div>
            <div>
              <span className="text-navy-muted">Expected Payout</span>
              <p className="text-navy font-semibold">{formatAmount(account.expected_payout)}</p>
            </div>
            <div>
              <span className="text-navy-muted">Start Date</span>
              <p className="text-navy">{formatDate(account.start_date)}</p>
            </div>
            <div>
              <span className="text-navy-muted">Maturity Date</span>
              <p className="text-navy">{formatDate(account.maturity_date)}</p>
            </div>
          </div>
        </div>

        <h2 className="text-navy font-semibold mb-3">
          Contributions ({paidCount}/{totalInstallments})
        </h2>

        {!isComplete && account.status === "active" && (
          <PayContributionForm
            accountNumber={account.account_number}
            monthlyAmount={account.plan_details?.monthly_amount ?? "0"}
          />
        )}

        <div className="bg-white border border-sage-mid divide-y divide-sage-mid mt-4 rounded-xl">
          {contributionList.length === 0 ? (
            <div className="px-5 py-8 text-center text-navy-muted text-sm">
              No contributions yet.
            </div>
          ) : (
            contributionList.map((c) => (
              <div key={c.id} className="flex items-center justify-between px-5 py-3">
                <div>
                  <span className="text-navy font-medium text-sm">
                    Installment #{c.installment_number}
                  </span>
                  <p className="text-xs text-navy-muted">{formatDate(c.paid_at)}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-navy font-semibold text-sm">{formatAmount(c.amount)}</span>
                  <Badge variant={c.status === "paid" ? "success" : "danger"}>{c.status}</Badge>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
