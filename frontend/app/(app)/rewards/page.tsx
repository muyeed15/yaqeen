"use client";

import { useState } from "react";
import useSWR, { useSWRConfig } from "swr";
import { ArrowDown, ArrowUp, Sparkles } from "lucide-react";
import { claimOfferAction } from "@/app/actions";
import { Button } from "@/components/ui/Button";
import { PageHeader } from "@/components/ui/PageHeader";
import type { Offer, PaginatedResponse, PointsTransaction, Reward } from "@/types";
import { formatDate, formatNumber } from "@/utils/helpers";

export default function RewardsPage() {
  const { data: reward } = useSWR<Reward>("/api/rewards");
  const { data: offers } = useSWR<Offer[]>("/api/offers");
  const { data: history } = useSWR<PaginatedResponse<PointsTransaction>>(
    "/api/points-history?page=1",
  );
  const { mutate: mutateAll } = useSWRConfig();
  const [message, setMessage] = useState("");
  const points = reward?.points ?? 0;

  return (
    <div>
      <PageHeader title="Rewards" subtitle="Yaqeen Points" showBack backHref="/dashboard" />
      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl space-y-6">
        <div className="relative overflow-hidden rounded-2xl bg-teal p-6 text-white shadow-lg shadow-teal/20 sm:p-7">
          <div className="absolute -right-8 -top-10 h-36 w-36 rounded-full border-[24px] border-white/10" />
          <div className="absolute -bottom-12 right-24 h-28 w-28 rounded-full bg-white/5" />
          <div className="relative flex items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 text-white/75">
                <Sparkles className="h-4 w-4" />
                <p className="text-[11px] font-semibold uppercase tracking-widest">
                  Available rewards
                </p>
              </div>
              <div className="mt-3 flex items-end gap-2">
                <p className="text-4xl font-bold leading-none tabular-nums sm:text-5xl">
                  {formatNumber(points)}
                </p>
                <p className="pb-1 text-sm font-semibold text-white/75">points</p>
              </div>
              <p className="mt-4 text-xs text-white/70">
                {formatNumber(reward?.lifetime_points ?? 0)} points earned since joining
              </p>
            </div>
          </div>
        </div>

        {message && (
          <p className="rounded-xl border border-teal/20 bg-teal/10 px-4 py-3 text-sm font-medium text-teal">
            {message}
          </p>
        )}

        <section>
          <div className="mb-3 flex items-end justify-between">
            <div>
              <p className="font-semibold text-navy">Available offers</p>
              <p className="text-xs text-navy-muted">Use points for exclusive benefits</p>
            </div>
            <p className="text-xs font-semibold text-teal">{offers?.length ?? 0} offers</p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {offers?.map((offer) => {
              const canClaim = points >= offer.points_required;
              return (
                <article
                  key={offer.id}
                  className="flex flex-col overflow-hidden rounded-2xl border border-sage-mid bg-white shadow-sm transition-shadow hover:shadow-md"
                >
                  <div className="flex-1 p-5">
                    <div className="mb-4 flex items-center justify-end">
                      <span className="rounded-full bg-sage px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide text-navy-muted">
                        {offer.category}
                      </span>
                    </div>
                    <h3 className="font-semibold text-navy">{offer.title}</h3>
                    <p className="mt-1.5 text-xs leading-relaxed text-navy-muted">
                      {offer.description}
                    </p>
                    {(Number(offer.cashback_amount) > 0 || Number(offer.cashback_pct) > 0) && (
                      <p className="mt-3 text-xs font-semibold text-teal">
                        {Number(offer.cashback_amount) > 0
                          ? `৳${offer.cashback_amount} cashback`
                          : `${offer.cashback_pct}% cashback`}
                      </p>
                    )}
                  </div>
                  <div className="border-t border-sage-mid bg-sage/30 p-4">
                    <div className="mb-3 flex items-center justify-between">
                      <span className="text-xs text-navy-muted">Cost</span>
                      <span className="text-sm font-bold text-teal">
                        {formatNumber(offer.points_required)} points
                      </span>
                    </div>
                    <Button
                      size="sm"
                      className="w-full"
                      disabled={!canClaim}
                      onClick={async () => {
                        const result = await claimOfferAction(offer.id);
                        setMessage(result.message);
                        await mutateAll(
                          (key) => typeof key === "string" && key.startsWith("/api/"),
                        );
                      }}
                    >
                      {canClaim
                        ? "Claim Offer"
                        : `Need ${formatNumber(offer.points_required - points)} more`}
                    </Button>
                  </div>
                </article>
              );
            })}
            {!offers?.length && (
              <p className="col-span-2 rounded-2xl border border-sage-mid bg-white py-14 text-center text-sm text-navy-muted">
                No active offers right now.
              </p>
            )}
          </div>
        </section>

        <section>
          <div className="mb-3">
            <p className="font-semibold text-navy">Points history</p>
            <p className="text-xs text-navy-muted">Your recent earning and redemption activity</p>
          </div>
          <div className="overflow-hidden rounded-2xl border border-sage-mid bg-white shadow-sm">
            {history?.results.map((item, index) => {
              const earned = item.transaction_type === "earn";
              const Icon = earned ? ArrowDown : ArrowUp;
              return (
                <div
                  key={item.id}
                  className={`flex items-center justify-between gap-3 p-4 ${index ? "border-t border-sage-mid" : ""}`}
                >
                  <div className="flex min-w-0 items-center gap-3">
                    <div
                      className={`grid h-9 w-9 shrink-0 place-items-center rounded-xl ${earned ? "bg-teal/10 text-teal" : "bg-sage text-navy-muted"}`}
                    >
                      <Icon className="h-4 w-4" />
                    </div>
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-navy">{item.reason}</p>
                      <p className="text-xs text-navy-muted">{formatDate(item.created_at)}</p>
                    </div>
                  </div>
                  <p
                    className={`shrink-0 font-bold tabular-nums ${earned ? "text-teal" : "text-navy-muted"}`}
                  >
                    {earned ? "+" : "-"}
                    {formatNumber(item.points)}
                  </p>
                </div>
              );
            })}
            {!history?.results.length && (
              <p className="py-14 text-center text-sm text-navy-muted">No points activity yet.</p>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
