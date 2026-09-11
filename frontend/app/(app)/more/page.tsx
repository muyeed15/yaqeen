import Link from "next/link";
import {
  Building2,
  CreditCard,
  FileText,
  Gift,
  Globe2,
  HandCoins,
  Heart,
  Landmark,
  LogOut,
  MessageCircle,
  Receipt,
  ShieldCheck,
  ShoppingCart,
  Smartphone,
  Ticket,
  User,
  Vault,
  Zap,
} from "lucide-react";
import { logoutAction } from "@/app/actions";
import { PageHeader } from "@/components/ui/PageHeader";

const ITEMS = [
  {
    href: "/money-requests",
    icon: HandCoins,
    label: "Money Requests",
    desc: "Request or respond to money",
  },

  { href: "/pay", icon: ShoppingCart, label: "Pay", desc: "Pay verified merchants" },
  { href: "/cards", icon: CreditCard, label: "Cards", desc: "Manage virtual cards" },
  { href: "/billpay", icon: Zap, label: "Pay Bills", desc: "Pay utility bills" },
  { href: "/recharge", icon: Smartphone, label: "Recharge", desc: "Mobile balance and data packs" },

  {
    href: "/banking",
    icon: Landmark,
    label: "Islamic Banking",
    desc: "Link accounts and move money",
  },
  { href: "/savings", icon: Vault, label: "Savings", desc: "Mudarabah savings plans" },
  { href: "/loans", icon: Building2, label: "Qard Hasan", desc: "Interest-free financing" },
  { href: "/remittance", icon: Globe2, label: "Remittance", desc: "Receive money from abroad" },

  { href: "/tickets", icon: Ticket, label: "Tickets", desc: "Book travel and events" },
  { href: "/rewards", icon: Gift, label: "Rewards", desc: "Points and available offers" },
  { href: "/charity", icon: Heart, label: "Charity", desc: "Zakat, Sadaqah & Hawl" },
  { href: "/support", icon: MessageCircle, label: "Support", desc: "Get help from our team" },

  { href: "/statements", icon: FileText, label: "Statements", desc: "Monthly account summaries" },
  { href: "/transactions", icon: Receipt, label: "History", desc: "View all transactions" },
  {
    href: "/account",
    icon: ShieldCheck,
    label: "KYC & Nominees",
    desc: "Identity and nominee details",
  },
  { href: "/profile", icon: User, label: "Profile", desc: "Account settings" },
];

export default function MorePage() {
  return (
    <div>
      <PageHeader title="More Services" subtitle="Explore" showBack backHref="/dashboard" />
      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl">
        <div className="space-y-2">
          {ITEMS.map(({ href, icon: Icon, label, desc }) => (
            <Link
              key={href}
              href={href}
              className="flex items-center gap-4 bg-white border border-sage-mid px-5 py-4 rounded-xl transition-colors active:bg-sage-mid/20"
            >
              <div className="h-10 w-10 bg-teal flex items-center justify-center shrink-0 rounded-lg">
                <Icon className="h-5 w-5 text-white" />
              </div>
              <div className="min-w-0">
                <p className="text-sm font-semibold text-navy">{label}</p>
                <p className="text-xs text-navy-muted">{desc}</p>
              </div>
            </Link>
          ))}
        </div>

        <form action={logoutAction} className="mt-8">
          <button
            type="submit"
            className="flex items-center gap-3 text-sm text-red-500 font-semibold w-full px-5 py-4 bg-white border border-sage-mid active:bg-red-50 transition-colors rounded-xl"
          >
            <LogOut className="h-5 w-5" />
            Sign Out
          </button>
        </form>
      </div>
    </div>
  );
}
