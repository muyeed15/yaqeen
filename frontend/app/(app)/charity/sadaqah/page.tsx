"use client";

import { useRouter } from "next/navigation";
import useSWR from "swr";
import {
  GraduationCap,
  HeartPulse,
  HandCoins,
  Users,
  Landmark,
  Droplets,
  LifeBuoy,
  Heart,
  History,
  ChevronRight,
  type LucideIcon,
} from "lucide-react";
import type { FoundationCategory } from "@/types";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageTransition } from "@/components/ui/PageTransition";

const CAUSE_ICONS: Record<string, LucideIcon> = {
  GraduationCap,
  HeartPulse,
  HandCoins,
  Users,
  Landmark,
  Droplets,
  LifeBuoy,
  Heart,
};

export default function SadaqahPage() {
  const router = useRouter();
  const { data } = useSWR<FoundationCategory[]>("/api/foundation-causes");
  const categories = data ?? [];

  return (
    <PageTransition>
      <div className="flex items-center justify-between">
        <PageHeader title="Give Sadaqah" subtitle="Charity" showBack backHref="/charity" />
      </div>

      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl">
        <p className="text-[11px] font-semibold uppercase tracking-widest text-navy-muted mb-3">
          Select Cause
        </p>

        {categories.length === 0 ? (
          <div className="bg-white border border-sage-mid px-6 py-16 text-center rounded-2xl shadow-sm">
            <Heart className="h-10 w-10 text-sage-mid mx-auto mb-3" strokeWidth={1.5} />
            <p className="text-navy font-semibold">No charity causes available</p>
            <p className="text-sm text-navy-muted mt-1">Please try again later.</p>
          </div>
        ) : (
          <div className="grid grid-cols-3 gap-3">
            {categories.map((cat) => {
              const Icon = CAUSE_ICONS[cat.icon] ?? Heart;
              return (
                <button
                  key={cat.key}
                  type="button"
                  onClick={() => router.push(`/charity/sadaqah/${cat.key}`)}
                  className="flex flex-col items-center gap-2 bg-white border border-sage-mid rounded-2xl p-5 hover:border-teal hover:shadow-sm active:scale-95 transition-all duration-150"
                >
                  <div className="h-12 w-12 bg-teal rounded-2xl flex items-center justify-center">
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <span className="text-xs font-semibold text-navy text-center">{cat.label}</span>
                  <span className="text-[10px] text-navy-muted">
                    {cat.count} {cat.count === 1 ? "foundation" : "foundations"}
                  </span>
                </button>
              );
            })}
          </div>
        )}

        <button
          type="button"
          onClick={() => router.push("/charity/sadaqah/history")}
          className="w-full flex items-center gap-3 bg-white border border-sage-mid rounded-2xl p-5 mt-6 hover:border-teal hover:shadow-sm active:scale-[0.99] transition-all duration-150"
        >
          <div className="h-12 w-12 bg-teal rounded-2xl flex items-center justify-center shrink-0">
            <History className="h-6 w-6 text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-navy">My Donation History</p>
            <p className="text-xs text-navy-muted">View your past sadaqah donations</p>
          </div>
          <ChevronRight className="h-5 w-5 text-navy-muted shrink-0" />
        </button>
      </div>
    </PageTransition>
  );
}
