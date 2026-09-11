import Link from "next/link";
import { CreditCard, Store } from "lucide-react";
import { getMe, getWallet, getCards } from "@/utils/api";
import { PageTransition } from "@/components/ui/PageTransition";
import { Button } from "@/components/ui/Button";
import { PageHeader } from "@/components/ui/PageHeader";
import { logoutAction } from "@/app/actions";
import { formatAmount, formatDate, getInitials } from "@/utils/helpers";

export default async function ProfilePage() {
  const [user, wallet, cardsData] = await Promise.all([getMe(), getWallet(), getCards(1)]);
  const activeCards = cardsData.results.filter((c) => c.status === "active").length;

  return (
    <PageTransition>
      <PageHeader title="Profile" subtitle="Account" showBack backHref="/dashboard" />

      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl space-y-5">
        {/* Identity */}
        <div className="bg-teal text-white px-6 py-5 flex items-center gap-5 rounded-xl">
          <div className="h-14 w-14 bg-white/20 flex items-center justify-center text-white text-xl font-bold shrink-0 rounded-full">
            {getInitials(user.full_name)}
          </div>
          <div>
            <p className="text-lg font-bold">{user.full_name}</p>
            <p className="text-white/70 text-sm">{user.phone}</p>
            <div className="flex gap-2 mt-2 flex-wrap">
              <span
                className={`text-xs font-semibold px-2 py-0.5 rounded-md ${user.is_verified ? "bg-white/20 text-white" : "bg-amber-400/30 text-amber-200"}`}
              >
                {user.is_verified ? "VERIFIED" : "UNVERIFIED"}
              </span>
              <span
                className={`text-xs font-semibold px-2 py-0.5 rounded-md ${user.is_active ? "bg-white/20 text-white" : "bg-red-400/30 text-red-200"}`}
              >
                {user.is_active ? "ACTIVE" : "INACTIVE"}
              </span>
              {user.has_merchant_profile && (
                <span className="text-xs font-semibold px-2 py-0.5 bg-teal/80 text-white flex items-center gap-1 rounded-md">
                  <Store className="h-3 w-3" aria-hidden="true" /> MERCHANT
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Personal info */}
        <div className="bg-white border border-sage-mid rounded-xl overflow-hidden">
          <div className="px-4 py-2 bg-sage border-b border-sage-mid">
            <p className="text-xs font-semibold uppercase tracking-widest text-navy-muted">
              Personal Information
            </p>
          </div>
          {[
            { label: "Full Name", value: user.full_name },
            { label: "Phone Number", value: user.phone },
            { label: "NID Number", value: user.nid },
            { label: "Member Since", value: formatDate(user.created_at) },
          ].map(({ label, value }, i, arr) => (
            <div
              key={label}
              className={`flex px-4 py-3 ${i < arr.length - 1 ? "border-b border-sage-mid" : ""}`}
            >
              <span className="text-xs font-semibold uppercase tracking-widest text-navy-muted w-36 shrink-0 mt-0.5">
                {label}
              </span>
              <span className="text-sm text-navy font-medium">{value}</span>
            </div>
          ))}
        </div>

        {/* Wallet */}
        <div className="bg-white border border-sage-mid rounded-xl overflow-hidden">
          <div className="px-4 py-2 bg-sage border-b border-sage-mid">
            <p className="text-xs font-semibold uppercase tracking-widest text-navy-muted">
              Wallet
            </p>
          </div>
          {[
            {
              label: "Balance",
              value: formatAmount(wallet.balance),
              bold: true,
            },
            {
              label: "Daily Limit",
              value: formatAmount(wallet.daily_limit),
              bold: false,
            },
            {
              label: "Status",
              value: wallet.status.toUpperCase(),
              bold: false,
            },
          ].map(({ label, value, bold }, i, arr) => (
            <div
              key={label}
              className={`flex px-4 py-3 ${i < arr.length - 1 ? "border-b border-sage-mid" : ""}`}
            >
              <span className="text-xs font-semibold uppercase tracking-widest text-navy-muted w-36 shrink-0 mt-0.5">
                {label}
              </span>
              <span className={`text-sm font-bold ${bold ? "text-navy" : "text-navy"}`}>
                {value}
              </span>
            </div>
          ))}
        </div>

        {/* Cards */}
        <Link
          href="/cards"
          className="bg-white border border-sage-mid flex items-center justify-between px-4 py-4 hover:bg-sage/30 transition-colors rounded-xl"
        >
          <div className="flex items-center gap-3">
            <CreditCard className="h-5 w-5 text-navy-muted" aria-hidden="true" />
            <div>
              <p className="text-sm font-semibold text-navy">My Cards</p>
              <p className="text-xs text-navy-muted">
                {activeCards > 0
                  ? `${activeCards} active card${activeCards !== 1 ? "s" : ""}`
                  : "No active cards"}
              </p>
            </div>
          </div>
          <span className="text-xs font-semibold text-navy">Manage</span>
        </Link>

        {/* Sign out */}
        <form action={logoutAction}>
          <Button
            type="submit"
            variant="destructive"
            size="md"
            className="w-full border border-red-500"
          >
            Sign Out
          </Button>
        </form>
      </div>
    </PageTransition>
  );
}
