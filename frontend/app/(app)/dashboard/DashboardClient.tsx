"use client";

import { useMemo } from "react";
import Link from "next/link";
import Image from "next/image";
import useSWR from "swr";
import { useAutoAnimate } from "@formkit/auto-animate/react";
import {
  Send,
  Banknote,
  Store,
  CreditCard,
  Receipt,
  Landmark,
  Vault,
  Heart,
  QrCode,
  Smartphone,
  Ticket,
  HandCoins,
  MessageCircle,
  CircleDollarSign,
  Globe2,
  Gift,
} from "lucide-react";
import type { Wallet, Transaction, PaginatedResponse } from "@/types";
import { formatAmount } from "@/utils/helpers";
import { TransactionCard } from "@/components/ui/TransactionCard";

const ACTIONS = [
  // Peer-to-peer money
  { label: "Send", icon: Send, href: "/send" },
  { label: "Receive", icon: QrCode, href: "/receive" },
  { label: "Requests", icon: CircleDollarSign, href: "/money-requests" },
  { label: "Cash Out", icon: Banknote, href: "/send" },

  // Everyday payments
  { label: "Pay", icon: Store, href: "/pay" },
  { label: "Cards", icon: CreditCard, href: "/cards" },
  { label: "Pay Bills", icon: Receipt, href: "/billpay" },
  { label: "Recharge", icon: Smartphone, href: "/recharge" },

  // Financial products
  { label: "Banking", icon: Landmark, href: "/banking" },
  { label: "Savings", icon: Vault, href: "/savings" },
  { label: "Qard Hasan", icon: HandCoins, href: "/loans" },
  { label: "Remittance", icon: Globe2, href: "/remittance" },

  // Additional services
  { label: "Tickets", icon: Ticket, href: "/tickets" },
  { label: "Rewards", icon: Gift, href: "/rewards" },
  { label: "Charity", icon: Heart, href: "/charity" },
  { label: "Support", icon: MessageCircle, href: "/support" },
];

type Props = {
  initialWallet: Wallet;
  initialTransactions: Transaction[];
  svgDataUri?: string;
  fullName?: string;
};

function sortDesc(txs: Transaction[]): Transaction[] {
  return [...txs].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
  );
}

export default function DashboardClient({
  initialWallet,
  initialTransactions,
  svgDataUri,
  fullName,
}: Props): React.ReactElement {
  const { data: wallet = initialWallet } = useSWR<Wallet>("/api/wallet", {
    fallbackData: initialWallet,
    revalidateOnMount: true,
    refreshInterval: 0,
  });
  const { data: txPage } = useSWR<PaginatedResponse<Transaction>>("/api/transactions?page=1", {
    refreshInterval: 0,
  });
  const rawTransactions = txPage?.results ?? initialTransactions;

  const transactions = useMemo(() => sortDesc(rawTransactions), [rawTransactions]);
  const myPhone = wallet.user_phone;
  const active = wallet.status === "active";
  const recentTx = useMemo(() => transactions.slice(0, 5), [transactions]);
  const [gridRef] = useAutoAnimate();
  const [listRef] = useAutoAnimate();

  return (
    <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl space-y-6">
      {/* Balance card */}
      <div className="bg-teal text-white py-10 pl-6 pr-6 sm:py-12 sm:pl-8 sm:pr-10 relative overflow-hidden rounded-2xl shadow-lg shadow-teal/20">
        {svgDataUri && (
          <Image
            src={svgDataUri}
            alt=""
            fill
            unoptimized
            className="object-cover object-top pointer-events-none"
          />
        )}
        <div className="relative flex flex-col justify-center">
          {fullName && (
            <p className="text-white/80 text-sm font-medium mb-3">
              Welcome back, <strong className="text-white">{fullName}</strong>
            </p>
          )}
          <p className="text-white/60 text-[11px] font-semibold uppercase tracking-widest mb-1">
            Balance
          </p>
          <p className="text-4xl sm:text-5xl font-bold tracking-tight leading-none tabular-nums">
            {formatAmount(wallet.balance)}
          </p>
        </div>
      </div>

      {/* Service grid */}
      <div>
        <p className="text-[11px] font-semibold uppercase tracking-widest text-navy-muted mb-3">
          Services
        </p>
        <div ref={gridRef} className="grid grid-cols-4 gap-2.5 sm:gap-3">
          {ACTIONS.map(({ label, icon: Icon, href }) => (
            <Link
              key={label}
              href={active ? href : "#"}
              aria-disabled={!active}
              className={`flex flex-col items-center justify-center gap-1.5 bg-teal text-white px-1 py-4 rounded-2xl transition-all duration-150 active:scale-95 active:opacity-80 ${
                !active ? "opacity-40 pointer-events-none" : "hover:shadow-md hover:shadow-teal/20"
              }`}
            >
              <Icon className="h-5 w-5 sm:h-6 sm:w-6 shrink-0" aria-hidden="true" />
              <span className="text-[10px] sm:text-[11px] font-semibold text-center leading-tight">
                {label}
              </span>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent Transactions */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <p className="text-[11px] font-semibold uppercase tracking-widest text-navy-muted">
            Recent Transactions
          </p>
          <Link
            href="/transactions"
            className="text-xs font-semibold text-teal active:opacity-50 transition-opacity"
          >
            View All
          </Link>
        </div>

        <div
          ref={listRef}
          className="bg-white border border-sage-mid divide-y divide-sage-mid rounded-2xl overflow-hidden shadow-sm"
        >
          {recentTx.length === 0 ? (
            <div className="text-center py-12">
              <Receipt className="h-8 w-8 text-sage-mid mx-auto mb-3" strokeWidth={1.5} />
              <p className="text-sm font-medium text-navy-muted">No transactions yet</p>
              <p className="text-xs text-navy-muted mt-1">Your recent activity will appear here.</p>
            </div>
          ) : (
            recentTx.map((tx) => (
              <TransactionCard key={tx.id} tx={tx} myPhone={myPhone} relativeTime />
            ))
          )}
        </div>
      </div>
    </div>
  );
}
