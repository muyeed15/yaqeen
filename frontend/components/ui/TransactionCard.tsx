import type { Transaction } from "@/types";
import {
  getTxMeta,
  formatAmount,
  formatRelativeTime,
  formatDate,
  STATUS_VARIANT,
} from "@/utils/helpers";
import { Badge } from "@/components/ui/Badge";

type Props = {
  tx: Transaction;
  myPhone: string;
  /** Show relative time (e.g. "5m ago") instead of full date */
  relativeTime?: boolean;
};

export function TransactionCard({ tx, myPhone, relativeTime = false }: Props): React.ReactElement {
  const meta = getTxMeta(tx, myPhone);

  return (
    <div className={`flex items-center justify-between px-4 py-3.5 transition-colors duration-100`}>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2 flex-wrap">
          <span className={`text-sm font-semibold ${meta.color}`}>{meta.label}</span>
          <Badge variant={STATUS_VARIANT[tx.status]}>
            {tx.status.charAt(0).toUpperCase() + tx.status.slice(1)}
          </Badge>
        </div>
        <p className="text-xs text-navy-muted mt-0.5 truncate">
          {meta.direction === "to" ? "To" : "From"}: {meta.counterparty}
        </p>
        {tx.note && <p className="text-xs text-navy-muted italic">{tx.note}</p>}
      </div>
      <div className="text-right shrink-0 ml-6">
        <p className={`text-sm font-bold tabular-nums ${meta.color}`}>
          {meta.minus ? "−" : "+"}
          {formatAmount(tx.amount)}
        </p>
        <p className="text-xs text-navy-muted" suppressHydrationWarning>
          {relativeTime ? formatRelativeTime(tx.created_at) : formatDate(tx.created_at)}
        </p>
      </div>
    </div>
  );
}
