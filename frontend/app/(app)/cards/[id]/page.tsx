"use client";

import { use, useState, useTransition } from "react";
import useSWR from "swr";
import { CreditCard, Snowflake } from "lucide-react";
import { blockCardAction, unblockCardAction } from "@/app/actions";
import { BackButton } from "@/components/ui/BackButton";
import type { Card, User, PaginatedResponse } from "@/types";
import Image from "next/image";

export default function CardDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data: cardsData, mutate } = useSWR<PaginatedResponse<Card>>("/api/cards?page=1");
  const { data: user } = useSWR<User>("/api/me");
  const card = cardsData?.results.find((c) => c.id === Number(id));
  const [freezing, startFreeze] = useTransition();
  const [confirmFreeze, setConfirmFreeze] = useState(false);

  const toggleFreeze = () => {
    if (!card) return;
    const action = card.status === "active" ? blockCardAction : unblockCardAction;
    startFreeze(async () => {
      await action(card.id);
      mutate();
      setConfirmFreeze(false);
    });
  };

  if (!card) {
    return (
      <div>
        <div className="bg-white px-4 h-16 flex items-center gap-3">
          <BackButton href="/cards" />
          <h1 className="text-navy font-bold text-lg">Card Details</h1>
        </div>
        <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl">
          <div className="bg-white border border-sage-mid px-6 py-16 text-center rounded-xl">
            <CreditCard className="h-10 w-10 text-navy-muted mb-3" strokeWidth={1.5} />
            <p className="text-navy font-semibold">Card not found</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="bg-white px-4 h-16 flex items-center gap-3">
        <BackButton href="/cards" />
        <h1 className="text-navy font-bold text-lg">Card Details</h1>
      </div>
      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl space-y-6">
        <div className="relative bg-gradient-to-br from-teal to-teal/80 text-white rounded-xl p-6 aspect-[1.586] flex flex-col justify-between shadow-lg overflow-hidden">
          <div className="absolute inset-0 opacity-10">
            <div className="absolute -top-10 -right-10 w-40 h-40 rounded-full border-[6px] border-white" />
            <div className="absolute -bottom-8 -left-8 w-32 h-32 rounded-full border-[4px] border-white" />
            <div className="absolute top-1/3 right-1/4 w-2 h-2 rounded-full bg-white" />
            <div className="absolute bottom-1/4 left-1/3 w-1.5 h-1.5 rounded-full bg-white" />
          </div>
          <div className="relative flex items-start justify-between">
            <div className="space-y-3">
              <p className="text-white/50 text-[10px] font-semibold tracking-[0.15em] uppercase">
                Yaqeen
              </p>
              <div className="h-10 w-12 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-xl flex items-center justify-center">
                <div className="grid grid-cols-3 gap-[1.5px]">
                  {[...Array(6)].map((_, i) => (
                    <div key={i} className="w-[3px] h-[5px] bg-yellow-200 rounded-[1px]" />
                  ))}
                </div>
              </div>
            </div>
            <Image src="/logo.svg" alt="" width={40} height={40} />
          </div>
          <div className="relative space-y-4">
            <p className="text-xl sm:text-2xl font-bold tracking-[0.25em] tabular-nums">
              •••• •••• •••• {card.last_four}
            </p>
            <div className="flex items-end justify-between">
              <div className="space-y-1">
                <p className="text-white/40 text-[9px] font-semibold tracking-[0.15em] uppercase">
                  Card Holder
                </p>
                <p className="text-sm font-semibold tracking-wide">
                  {user?.full_name ?? "Cardholder"}
                </p>
              </div>
              <div className="text-right space-y-1">
                <p className="text-white/40 text-[9px] font-semibold tracking-[0.15em] uppercase">
                  Expires
                </p>
                <p className="text-sm font-semibold">
                  {String(card.expiry_month).padStart(2, "0")}/{card.expiry_year}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white border border-sage-mid rounded-xl overflow-hidden">
          <div className="px-4 py-2 bg-sage border-b border-sage-mid">
            <p className="text-xs font-semibold uppercase tracking-widest text-navy-muted">
              Card Information
            </p>
          </div>
          <div className="divide-y divide-sage-mid">
            <div className="flex items-center justify-between px-4 py-3">
              <span className="text-xs text-navy-muted">Card Holder</span>
              <span className="text-sm font-semibold text-navy">{user?.full_name ?? "-"}</span>
            </div>
            <div className="flex items-center justify-between px-4 py-3">
              <span className="text-xs text-navy-muted">Status</span>
              <span
                className={`text-sm font-semibold ${
                  card.status === "active"
                    ? "text-teal"
                    : card.status === "blocked"
                      ? "text-red-500"
                      : "text-navy-muted"
                }`}
              >
                {card.status.charAt(0).toUpperCase() + card.status.slice(1)}
              </span>
            </div>
            <div className="flex items-center justify-between px-4 py-3">
              <span className="text-xs text-navy-muted">Card Number</span>
              <span className="text-sm font-semibold text-navy tabular-nums">
                •••• •••• •••• {card.last_four}
              </span>
            </div>
            <div className="flex items-center justify-between px-4 py-3">
              <span className="text-xs text-navy-muted">Type</span>
              <span className="text-sm font-semibold text-navy">
                {card.card_type === "debit" ? "Debit Card" : "Prepaid Card"}
              </span>
            </div>
            <div className="flex items-center justify-between px-4 py-3">
              <span className="text-xs text-navy-muted">Expiry</span>
              <span className="text-sm font-semibold text-navy">
                {String(card.expiry_month).padStart(2, "0")}/{card.expiry_year}
              </span>
            </div>
          </div>
        </div>

        {confirmFreeze && (
          <div
            className="fixed inset-0 z-50 flex items-center justify-center px-4 bg-navy/60"
            onClick={() => setConfirmFreeze(false)}
          >
            <div
              className="bg-white w-full max-w-sm rounded-xl overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6 text-center space-y-3">
                <div
                  className={`h-12 w-12 rounded-full flex items-center justify-center ${
                    card.status === "active" ? "bg-red-100" : "bg-teal/10"
                  }`}
                >
                  <Snowflake
                    className={`h-6 w-6 ${card.status === "active" ? "text-red-500" : "text-teal"}`}
                  />
                </div>
                <p className="text-navy font-bold text-base">
                  {card.status === "active" ? "Freeze Card?" : "Unfreeze Card?"}
                </p>
                <p className="text-sm text-navy-muted">
                  {card.status === "active"
                    ? "Frozen cards cannot be used for transactions until unfrozen."
                    : "The card will be reactivated for transactions."}
                </p>
              </div>
              <div className="flex border-t border-sage-mid">
                <button
                  type="button"
                  onClick={() => setConfirmFreeze(false)}
                  className="flex-1 py-4 text-sm font-semibold text-navy border-r border-sage-mid active:opacity-70 transition-opacity"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  disabled={freezing}
                  onClick={toggleFreeze}
                  className={`flex-1 py-4 text-sm font-semibold flex items-center justify-center gap-2 transition-opacity disabled:opacity-40 ${
                    card.status === "active"
                      ? "text-red-500 active:opacity-70"
                      : "text-teal active:opacity-70"
                  }`}
                >
                  {freezing ? (
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                  ) : null}
                  {card.status === "active" ? "Yes, Freeze" : "Yes, Unfreeze"}
                </button>
              </div>
            </div>
          </div>
        )}

        <button
          type="button"
          onClick={() => setConfirmFreeze(true)}
          className={`w-full py-4 text-sm font-semibold rounded-xl flex items-center justify-center gap-2 transition-opacity active:opacity-80 ${
            card.status === "active" ? "bg-red-500 text-white" : "bg-teal text-white"
          }`}
        >
          <Snowflake className="h-4 w-4" />
          {card.status === "active" ? "Freeze Card" : "Unfreeze Card"}
        </button>
      </div>
    </div>
  );
}
