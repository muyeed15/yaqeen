import { getWallet, getTransactions } from "@/utils/api";
import { formatAmount, formatDate, getTxMeta, STATUS_VARIANT } from "@/utils/helpers";
import { PageTransition } from "@/components/ui/PageTransition";
import { Badge } from "@/components/ui/Badge";
import { TransactionCard } from "@/components/ui/TransactionCard";
import { PageHeader } from "@/components/ui/PageHeader";
import { PaginationUrl } from "@/components/ui/PaginationUrl";

export default async function TransactionsPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>;
}): Promise<React.ReactElement> {
  const { page: rawPage } = await searchParams;
  const currentPage = Math.max(1, parseInt(rawPage ?? "1") || 1);

  const [wallet, txData] = await Promise.all([getWallet(), getTransactions(currentPage)]);
  const myPhone = wallet.user_phone;
  const { results: transactions, total_pages: totalPages, count } = txData;

  return (
    <PageTransition>
      <PageHeader title="Transactions" subtitle="History" showBack backHref="/dashboard" />

      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl">
        {transactions.length === 0 ? (
          <div className="bg-white border border-sage-mid px-6 py-16 text-center rounded-xl">
            <p className="text-navy font-semibold">No transactions yet</p>
            <p className="text-sm text-navy-muted mt-1">
              Your transaction history will appear here.
            </p>
          </div>
        ) : (
          <>
            {/* Desktop table */}
            <div className="hidden sm:block bg-white border border-sage-mid overflow-hidden rounded-xl">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="bg-sage border-b border-sage-mid text-left">
                    {["Type", "Counterparty", "Status", "Date", "Amount"].map((h, i) => (
                      <th
                        key={h}
                        scope="col"
                        className={`px-4 py-3 text-[10px] font-semibold uppercase tracking-widest text-navy-muted whitespace-nowrap ${i === 4 ? "text-right" : ""}`}
                      >
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-sage-mid">
                  {transactions.map((tx) => {
                    const meta = getTxMeta(tx, myPhone);
                    return (
                      <tr key={tx.id} className="hover:bg-sage/40 transition-colors duration-100">
                        <td className="px-4 py-3">
                          <span className={`font-semibold ${meta.color}`}>{meta.label}</span>
                        </td>
                        <td className="px-4 py-3 text-navy-muted max-w-[200px]">
                          <span className="text-xs text-navy-muted/70 uppercase tracking-wide">
                            {meta.direction === "to" ? "To" : "From"}
                          </span>
                          <span className="block font-medium text-navy truncate">
                            {meta.counterparty}
                          </span>
                          {tx.note && (
                            <span className="text-xs italic text-navy-muted/70">{tx.note}</span>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <Badge variant={STATUS_VARIANT[tx.status]}>
                            {tx.status.charAt(0).toUpperCase() + tx.status.slice(1)}
                          </Badge>
                        </td>
                        <td className="px-4 py-3 text-navy-muted whitespace-nowrap text-xs">
                          {formatDate(tx.created_at)}
                        </td>
                        <td className="px-4 py-3 text-right whitespace-nowrap">
                          <span className={`font-bold tabular-nums ${meta.color}`}>
                            {meta.minus ? "−" : "+"}
                            {formatAmount(tx.amount)}
                          </span>
                          {parseFloat(tx.fee) > 0 && (
                            <span className="block text-xs text-navy-muted">
                              Fee {formatAmount(tx.fee)}
                            </span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Mobile list */}
            <div className="sm:hidden bg-white border border-sage-mid divide-y divide-sage-mid rounded-xl">
              {transactions.map((tx) => (
                <TransactionCard key={tx.id} tx={tx} myPhone={myPhone} />
              ))}
            </div>

            <p className="text-xs text-navy-muted mt-3 text-right">
              {count} transaction
              {count !== 1 ? "s" : ""} total
            </p>
            <PaginationUrl page={currentPage} totalPages={totalPages} />
          </>
        )}
      </div>
    </PageTransition>
  );
}
