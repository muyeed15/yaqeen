"use client";

import { useRouter } from "next/navigation";
import useSWR from "swr";
import type { Operator } from "@/types";
import { EntityLogo } from "@/components/ui/EntityLogo";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageTransition } from "@/components/ui/PageTransition";

export default function RechargePage() {
  const router = useRouter();
  const { data } = useSWR<Operator[]>("/api/operators");
  const operators = data ?? [];

  return (
    <PageTransition>
      <PageHeader title="Mobile Recharge" subtitle="Top Up" showBack backHref="/dashboard" />

      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl">
        <p className="text-[11px] font-semibold uppercase tracking-widest text-navy-muted mb-3">
          Select Operator
        </p>

        {operators.length === 0 ? (
          <div className="bg-white border border-sage-mid px-6 py-16 text-center rounded-2xl shadow-sm">
            <p className="text-navy font-semibold">No operators available</p>
            <p className="text-sm text-navy-muted mt-1">Please try again later.</p>
          </div>
        ) : (
          <div className="grid grid-cols-3 gap-3">
            {operators.map((op) => (
              <button
                key={op.id}
                type="button"
                onClick={() => router.push(`/recharge/${op.id}`)}
                className="flex flex-col items-center gap-2 bg-white border border-sage-mid rounded-2xl p-5 hover:border-teal hover:shadow-sm active:scale-95 transition-all duration-150"
              >
                <EntityLogo logo={op.logo} name={op.name} />
                <span className="text-xs font-semibold text-navy text-center">{op.name}</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </PageTransition>
  );
}
