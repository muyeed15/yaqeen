"use client";

import { useActionState } from "react";
import { useRouter } from "next/navigation";
import useSWR from "swr";
import { Bus, Train, Plane, Film, Calendar, Ship, Ticket } from "lucide-react";
import { cancelTicketAction } from "@/app/actions";
import { useMutateOnSuccess } from "@/hooks/useMutateOnSuccess";
import type { TicketCategory, TicketBooking } from "@/types";
import { Button } from "@/components/ui/Button";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageTransition } from "@/components/ui/PageTransition";

const BADGE_COLORS: Record<string, string> = {
  confirmed: "bg-green-100 text-green-700",
  cancelled: "bg-red-100 text-red-700",
  refunded: "bg-yellow-100 text-yellow-700",
  pending: "bg-gray-100 text-gray-700",
};

const CATEGORY_META: Record<string, { icon: typeof Bus }> = {
  bus: { icon: Bus },
  train: { icon: Train },
  airline: { icon: Plane },
  ferry: { icon: Ship },
  cinema: { icon: Film },
  event: { icon: Calendar },
};

const initCancel = { ok: false, message: "" };

export default function TicketsPage() {
  const router = useRouter();
  const [cancelState, cancelAction, cancelPending] = useActionState(cancelTicketAction, initCancel);
  useMutateOnSuccess(cancelState.ok);
  const { data: categoryData } = useSWR<TicketCategory[]>("/api/ticket-categories");
  const { data: bookingData } = useSWR<{ results: TicketBooking[] }>("/api/tickets?page=1");
  const categories = categoryData ?? [];
  const bookings = bookingData?.results ?? [];

  return (
    <PageTransition>
      <PageHeader title="Tickets" subtitle="Book" showBack backHref="/dashboard" />

      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl space-y-8">
        {cancelState.message && (
          <div
            className={`rounded-xl px-4 py-3 text-sm font-medium ${
              cancelState.ok
                ? "bg-teal/10 border border-teal/30 text-teal"
                : "border-l-4 border-red-500 bg-red-50 text-red-700"
            }`}
          >
            {cancelState.message}
          </div>
        )}

        <div>
          <p className="text-[11px] font-semibold uppercase tracking-widest text-navy-muted mb-3">
            Select Category
          </p>

          {categories.length === 0 ? (
            <div className="bg-white border border-sage-mid px-6 py-16 text-center rounded-2xl shadow-sm">
              <p className="text-navy font-semibold">No tickets available</p>
              <p className="text-sm text-navy-muted mt-1">Please try again later.</p>
            </div>
          ) : (
            <div className="grid grid-cols-3 gap-3">
              {categories.map((cat) => {
                const meta = CATEGORY_META[cat.key] ?? { icon: Ticket };
                const Icon = meta.icon;
                return (
                  <button
                    key={cat.key}
                    type="button"
                    onClick={() => router.push(`/tickets/${cat.key}`)}
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

        {bookings.length > 0 && (
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-widest text-navy-muted mb-3">
              My Bookings
            </p>
            <div className="bg-white border border-sage-mid rounded-2xl divide-y divide-sage-mid overflow-hidden shadow-sm">
              {bookings.map((b) => (
                <div key={b.id} className="p-5">
                  <div className="flex items-start justify-between">
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-semibold text-navy">
                        {b.trip_name || b.provider_name}
                      </p>
                      {b.origin ? (
                        <p className="text-xs text-navy-muted mt-0.5">
                          {b.origin} &rarr; {b.destination}
                        </p>
                      ) : null}
                      <p className="text-xs text-navy-muted">
                        {b.journey_date}
                        {b.departure_time ? ` \u00B7 ${b.departure_time}` : ""}
                        {b.passengers > 1 ? ` \u00B7 ${b.passengers} pax` : ""}
                      </p>
                      {b.coach_class ? (
                        <p className="text-xs text-navy-muted">
                          {b.coach_class}
                          {b.seat_number ? ` \u00B7 ${b.seat_number}` : ""}
                        </p>
                      ) : null}
                      <div className="flex items-center gap-3 mt-2">
                        <p className="text-sm font-semibold text-navy">৳{b.amount}</p>
                        <p className="text-[10px] text-navy-muted">Ref: {b.booking_reference}</p>
                      </div>
                    </div>
                    <span
                      className={`text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded shrink-0 ${
                        BADGE_COLORS[b.status] ?? "bg-gray-100 text-gray-700"
                      }`}
                    >
                      {b.status}
                    </span>
                  </div>
                  {b.status === "confirmed" && (
                    <form action={cancelAction} className="mt-3">
                      <input type="hidden" name="ticket_id" value={b.id} />
                      <Button type="submit" loading={cancelPending} variant="secondary" size="sm">
                        Cancel{b.origin ? " (70% refund)" : ""}
                      </Button>
                    </form>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </PageTransition>
  );
}
