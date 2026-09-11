"use client";

import { useRouter } from "next/navigation";
import useSWR from "swr";
import { Zap, Flame, Droplets, Wifi, Tv, GraduationCap, Landmark } from "lucide-react";
import type { BillerCategory } from "@/types";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageTransition } from "@/components/ui/PageTransition";

const CATEGORY_META: Record<string, { icon: typeof Zap }> = {
  electricity: { icon: Zap },
  gas: { icon: Flame },
  water: { icon: Droplets },
  internet: { icon: Wifi },
  tv: { icon: Tv },
  education: { icon: GraduationCap },
  microfinance: { icon: Landmark },
};

export default function BillPayPage() {
  const router = useRouter();
  const { data } = useSWR<BillerCategory[]>("/api/biller-categories");
  const categories = data ?? [];

  return (
    <PageTransition>
      <PageHeader title="Pay Bills" subtitle="Utilities" showBack backHref="/dashboard" />

      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl">
        <p className="text-[11px] font-semibold uppercase tracking-widest text-navy-muted mb-3">
          Select Category
        </p>

        {categories.length === 0 ? (
          <div className="bg-white border border-sage-mid px-6 py-16 text-center rounded-2xl shadow-sm">
            <p className="text-navy font-semibold">No billers available</p>
            <p className="text-sm text-navy-muted mt-1">Please try again later.</p>
          </div>
        ) : (
          <div className="grid grid-cols-3 gap-3">
            {categories.map((cat) => {
              const meta = CATEGORY_META[cat.key] ?? { icon: Landmark };
              const Icon = meta.icon;
              return (
                <button
                  key={cat.key}
                  type="button"
                  onClick={() => router.push(`/billpay/${cat.key}`)}
                  className="flex flex-col items-center gap-2 bg-white border border-sage-mid rounded-2xl p-5 hover:border-teal hover:shadow-sm active:scale-95 transition-all duration-150"
                >
                  <div className="h-12 w-12 bg-teal rounded-2xl flex items-center justify-center">
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <span className="text-xs font-semibold text-navy text-center">{cat.label}</span>
                  <span className="text-[10px] text-navy-muted">
                    {cat.count} {cat.count === 1 ? "provider" : "providers"}
                  </span>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </PageTransition>
  );
}
