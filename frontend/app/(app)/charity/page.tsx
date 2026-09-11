import Link from "next/link";
import { Heart, Calculator, Clock, HandHelping, RefreshCw, List } from "lucide-react";
import { PageHeader } from "@/components/ui/PageHeader";

const SECTIONS = [
  {
    href: "/charity/zakat",
    icon: Calculator,
    label: "Calculate Zakat",
    desc: "Calculate zakat on your wealth",
  },
  {
    href: "/charity/zakat/pay",
    icon: Heart,
    label: "Pay Zakat",
    desc: "Pay zakat to verified foundations",
  },
  {
    href: "/charity/zakat/history",
    icon: Clock,
    label: "Zakat History",
    desc: "View your past zakat payments",
  },
  {
    href: "/charity/sadaqah",
    icon: HandHelping,
    label: "Give Sadaqah",
    desc: "Make voluntary donations",
  },
  {
    href: "/charity/hawl",
    icon: RefreshCw,
    label: "Hawl Tracking",
    desc: "Track your zakat eligibility",
  },
  {
    href: "/charity/sadaqah-jariyah",
    icon: List,
    label: "Sadaqah Jariyah",
    desc: "Manage recurring donations",
  },
];

export default function CharityPage() {
  return (
    <div>
      <PageHeader title="Charity" subtitle="Zakat & Sadaqah" showBack backHref="/dashboard" />

      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl grid gap-4 sm:grid-cols-2">
        {SECTIONS.map((s) => {
          const Icon = s.icon;
          return (
            <Link
              key={s.href}
              href={s.href}
              className="bg-white border border-sage-mid p-5 transition-colors rounded-xl"
            >
              <Icon className="h-6 w-6 text-navy-muted mb-3" />
              <h3 className="text-navy font-semibold text-sm">{s.label}</h3>
              <p className="text-navy-muted text-xs mt-1">{s.desc}</p>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
