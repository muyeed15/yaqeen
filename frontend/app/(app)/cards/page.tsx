"use client";

import { useActionState, useState, useEffect } from "react";
import Link from "next/link";
import useSWR from "swr";
import { ArrowRight, CreditCard, Plus, X } from "lucide-react";
import { addCardAction } from "@/app/actions";
import type { Card, PaginatedResponse } from "@/types";
import { Pagination } from "@/components/ui/Pagination";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Button } from "@/components/ui/Button";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageTransition } from "@/components/ui/PageTransition";

const initialState = { error: null, success: false };

export default function CardsPage() {
  const [page, setPage] = useState(1);
  const { data, mutate } = useSWR<PaginatedResponse<Card>>(`/api/cards?page=${page}`);
  const cards = data?.results ?? [];
  const totalPages = data?.total_pages ?? 1;
  const [showForm, setShowForm] = useState(false);
  const [state, formAction, pending] = useActionState(addCardAction, initialState);
  useEffect(() => {
    if (state.success) {
      mutate();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.success]);

  if (state.success && showForm) {
    setShowForm(false);
  }

  return (
    <PageTransition>
      <PageHeader showBack backHref="/dashboard">
        <div className="flex-1">
          <p className="text-[10px] text-navy-muted font-semibold uppercase tracking-widest leading-none">
            Payment Methods
          </p>
          <h1 className="text-navy font-bold text-lg leading-tight mt-0.5">My Cards</h1>
        </div>
        <button
          type="button"
          onClick={() => setShowForm((v) => !v)}
          aria-label={showForm ? "Cancel" : "Add card"}
          className="flex items-center gap-1.5 text-xs font-semibold text-navy active:opacity-60 transition-opacity"
        >
          {showForm ? (
            <>
              <X className="h-4 w-4" aria-hidden="true" /> Cancel
            </>
          ) : (
            <>
              <Plus className="h-4 w-4" aria-hidden="true" /> Add Card
            </>
          )}
        </button>
      </PageHeader>

      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl space-y-5">
        {showForm && (
          <form action={formAction} className="bg-white border border-sage-mid rounded-xl p-5">
            <p className="text-xs font-semibold uppercase tracking-widest text-navy-muted mb-4">
              Add New Card
            </p>

            {state.error && (
              <div className="mx-5 mt-4 border-l-4 border-red-500 bg-red-50 px-4 py-3 text-sm text-red-700">
                {state.error}
              </div>
            )}

            <div>
              <div className="py-4">
                <Input
                  label="Card Number"
                  name="card_number"
                  type="text"
                  inputMode="numeric"
                  maxLength={19}
                  required
                  placeholder="e.g. 4234 5678 9012 3456"
                />
              </div>
              <div className="py-4">
                <Select name="card_type" label="Card Type" required>
                  <option value="debit">Debit Card</option>
                  <option value="prepaid">Prepaid Card</option>
                </Select>
              </div>
              <div className="py-4 grid grid-cols-2 gap-4">
                <Input
                  label="Expiry Month"
                  name="expiry_month"
                  type="number"
                  min={1}
                  max={12}
                  required
                  placeholder="MM"
                />
                <Input
                  label="Expiry Year"
                  name="expiry_year"
                  type="number"
                  min={2024}
                  required
                  placeholder="YYYY"
                />
              </div>
            </div>

            <div className="flex gap-3 pt-4">
              <Button
                type="submit"
                variant="primary"
                loading={pending}
                className="flex-1 h-auto py-4 text-base rounded-xl"
              >
                {pending ? "Adding…" : "Add Card"}
              </Button>
            </div>
          </form>
        )}

        {cards.length === 0 && !showForm ? (
          <div className="bg-white border border-sage-mid px-6 py-16 text-center rounded-xl">
            <CreditCard className="h-10 w-10 text-navy-muted mx-auto mb-3" strokeWidth={1.5} />
            <p className="text-navy font-semibold">No cards linked</p>
            <p className="text-sm text-navy-muted mt-1">Add a card to get started.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {cards.map((card) => (
              <Link
                key={card.id}
                href={`/cards/${card.id}`}
                className="bg-teal text-white px-6 py-5 flex items-center justify-between rounded-xl hover:bg-teal/90 transition-colors"
              >
                <div>
                  <p className="text-white/50 text-xs font-semibold tracking-widest uppercase mb-1">
                    {card.card_type === "debit" ? "Debit Card" : "Prepaid Card"}
                  </p>
                  <p className="text-xl font-bold tracking-widest tabular-nums">
                    •••• •••• •••• {card.last_four}
                  </p>
                  <p className="text-white/60 text-xs mt-2">
                    Expires {String(card.expiry_month).padStart(2, "0")}/{card.expiry_year}
                  </p>
                </div>
                <div className="flex flex-col items-end gap-3">
                  <span
                    className={`text-xs font-semibold px-2 py-0.5 rounded-md ${
                      card.status === "active"
                        ? "bg-white/20 text-white"
                        : card.status === "blocked"
                          ? "bg-red-400/30 text-red-200"
                          : "bg-white/10 text-white/60"
                    }`}
                  >
                    {card.status.charAt(0).toUpperCase() + card.status.slice(1)}
                  </span>
                  <ArrowRight className="h-4 w-4 text-white/40" />
                </div>
              </Link>
            ))}
          </div>
        )}
        <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
      </div>
    </PageTransition>
  );
}
