"use client";

import { useRouter, useParams } from "next/navigation";
import useSWR from "swr";
import { ArrowLeft, ChevronRight } from "lucide-react";
import type { TicketProvider } from "@/types";
import { EntityLogo } from "@/components/ui/EntityLogo";
import { PageTransition } from "@/components/ui/PageTransition";

export default function TicketProvidersPage() {
  const { category } = useParams<{ category: string }>();
  const router = useRouter();
  const { data } = useSWR<TicketProvider[]>(
    `/api/ticket-providers?category=${encodeURIComponent(category)}`,
  );
  const providers = data ?? [];

  const label =
    providers[0]?.category_label ?? category.charAt(0).toUpperCase() + category.slice(1);

  return (
    <PageTransition>
      <div className="bg-white px-4 h-16 flex items-center gap-3 border-b border-sage/80">
        <button
          type="button"
          onClick={() => router.push("/tickets")}
          aria-label="Go back"
          className="text-navy-muted hover:text-navy active:scale-90 transition-all duration-150"
        >
          <ArrowLeft className="h-5 w-5" aria-hidden="true" />
        </button>
        <div>
          <p className="text-[10px] text-navy-muted font-semibold uppercase tracking-widest leading-none">
            Tickets
          </p>
          <h1 className="text-navy font-bold text-lg leading-tight mt-0.5">{label}</h1>
        </div>
      </div>

      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl">
        {providers.length === 0 ? (
          <div className="bg-white border border-sage-mid px-6 py-16 text-center rounded-2xl shadow-sm">
            <p className="text-navy font-semibold">No providers available</p>
            <p className="text-sm text-navy-muted mt-1">No {label} providers at this time.</p>
          </div>
        ) : (
          <div className="bg-white border border-sage-mid divide-y divide-sage-mid rounded-2xl overflow-hidden shadow-sm">
            {providers.map((p) => (
              <button
                key={p.id}
                type="button"
                onClick={() => router.push(`/tickets/${category}/${p.id}`)}
                className="w-full flex items-center gap-3 px-4 py-4 text-left hover:bg-sage/30 active:opacity-70 transition-colors"
              >
                <EntityLogo logo={p.logo} name={p.name} className="h-10 w-10" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-navy">{p.name}</p>
                  <p className="text-xs text-navy-muted">
                    {p.trips.length} {p.trips.length === 1 ? "trip" : "trips"}
                  </p>
                </div>
                <ChevronRight className="h-5 w-5 text-navy-muted shrink-0" />
              </button>
            ))}
          </div>
        )}
      </div>
    </PageTransition>
  );
}
