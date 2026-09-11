"use client";

import { useActionState, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import useSWR from "swr";
import { ArrowLeft, Info } from "lucide-react";
import { bookTicketAction } from "@/app/actions";
import type { TicketProvider } from "@/types";
import { EntityLogo } from "@/components/ui/EntityLogo";
import { DateChips } from "@/components/ui/DateChips";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import SeatPicker from "@/components/ui/SeatPicker";
import { PageTransition } from "@/components/ui/PageTransition";
import { formatAmount, calculateTicketTotal } from "@/utils/helpers";

const initBook = { ok: false, message: "" };

export default function BookTicketPage() {
  const { category, providerId } = useParams<{
    category: string;
    providerId: string;
  }>();
  const router = useRouter();
  const [bookState, bookAction, bookPending] = useActionState(bookTicketAction, initBook);
  const [selectedTripId, setSelectedTripId] = useState<number>(0);
  const [seats, setSeats] = useState<string[]>([]);
  const [passengerCount, setPassengerCount] = useState(1);
  const [journeyDate, setJourneyDate] = useState(() => {
    const d = new Date();
    d.setHours(0, 0, 0, 0);
    d.setDate(d.getDate() + 3);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(
      d.getDate(),
    ).padStart(2, "0")}`;
  });

  const { data } = useSWR<TicketProvider[]>(
    `/api/ticket-providers?category=${encodeURIComponent(category)}`,
  );
  const provider = (data ?? []).find((p) => p.id === Number(providerId)) ?? null;
  const trips = provider?.trips ?? [];
  const selectedTrip = trips.find((t) => t.id === selectedTripId) ?? null;

  const isTravel = ["bus", "train", "airline", "ferry"].includes(category);
  const hasSeats = ["bus", "train", "airline", "ferry", "cinema"].includes(category);

  // Passengers drive the total: selected seats for seat-based categories, the
  // ticket count otherwise (minimum one).
  const passengers = hasSeats ? Math.max(seats.length, 1) : passengerCount;
  const totalAmount = selectedTrip ? calculateTicketTotal(selectedTrip.price, passengers) : 0;

  return (
    <PageTransition>
      <div className="bg-white px-4 h-16 flex items-center gap-3 border-b border-sage/80">
        <button
          type="button"
          onClick={() => router.push(`/tickets/${category}`)}
          aria-label="Go back"
          className="text-navy-muted hover:text-navy active:scale-90 transition-all duration-150"
        >
          <ArrowLeft className="h-5 w-5" aria-hidden="true" />
        </button>
        <div>
          <p className="text-[10px] text-navy-muted font-semibold uppercase tracking-widest leading-none">
            Tickets
          </p>
          <h1 className="text-navy font-bold text-lg leading-tight mt-0.5">
            {provider?.name ?? "Book"}
          </h1>
        </div>
      </div>

      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl space-y-5">
        {bookState.message && (
          <div
            className={`rounded-xl px-4 py-3 text-sm font-medium ${
              bookState.ok
                ? "bg-teal/10 border border-teal/30 text-teal"
                : "border-l-4 border-red-500 bg-red-50 text-red-700"
            }`}
          >
            {bookState.message}
          </div>
        )}

        {provider && (
          <div className="bg-white border border-sage-mid rounded-2xl p-5 shadow-sm">
            <div className="flex items-center gap-3">
              <EntityLogo logo={provider.logo} name={provider.name} />
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-widest text-navy-muted">
                  Provider
                </p>
                <p className="text-sm font-semibold text-navy">{provider.name}</p>
              </div>
            </div>

            <div className="mt-5">
              <DateChips
                label={isTravel ? "Select Journey Date" : "Select Show Date"}
                onSelect={setJourneyDate}
              />
            </div>

            <p className="text-[11px] font-semibold uppercase tracking-widest text-navy-muted mt-5 mb-2">
              {isTravel ? "Select Trip" : "Select Show/Event"}
            </p>
            {trips.length === 0 ? (
              <p className="text-sm text-navy-muted">
                No {isTravel ? "trips" : "shows"} available.
              </p>
            ) : (
              <div className="space-y-2">
                {trips.map((t) => {
                  const isSelected = selectedTripId === t.id;
                  return (
                    <label
                      key={t.id}
                      className={`flex items-start gap-3 border rounded-xl p-4 cursor-pointer hover:border-teal/50 transition-all duration-150 ${
                        isSelected ? "border-teal bg-teal/5 shadow-sm" : "border-sage-mid"
                      }`}
                    >
                      <input
                        type="radio"
                        name="trip_radio"
                        checked={isSelected}
                        onChange={() => {
                          setSelectedTripId(t.id);
                          setSeats([]);
                        }}
                        className="accent-teal mt-0.5"
                      />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-navy">{t.name}</p>
                        <div className="flex flex-wrap gap-x-3 gap-y-0.5 mt-1">
                          {t.origin ? (
                            <span className="text-xs text-navy-muted">
                              {t.origin} &rarr; {t.destination}
                            </span>
                          ) : null}
                          <span className="text-xs text-navy-muted">{t.departure_time}</span>
                          {t.arrival_time ? (
                            <span className="text-xs text-navy-muted">&rarr; {t.arrival_time}</span>
                          ) : null}
                          <span className="text-xs text-navy-muted">{t.coach_class}</span>
                        </div>
                      </div>
                      <p className="text-sm font-bold text-navy whitespace-nowrap">৳{t.price}</p>
                    </label>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {selectedTrip && (
          <form
            action={bookAction}
            className="bg-white border border-sage-mid rounded-2xl p-5 shadow-sm space-y-5"
          >
            <div className="flex gap-2 items-start">
              <Info className="h-4 w-4 mt-0.5 shrink-0 text-navy-muted" />
              <p className="text-xs leading-snug text-navy-muted">
                {isTravel
                  ? "Travel tickets confirmed instantly. 70% refund on cancellation."
                  : "Tickets confirmed instantly."}
              </p>
            </div>

            <input type="hidden" name="provider_id" value={providerId} />
            <input type="hidden" name="trip_id" value={selectedTrip.id} />
            <input type="hidden" name="trip_name" value={selectedTrip.name} />
            <input type="hidden" name="departure_time" value={selectedTrip.departure_time} />
            <input type="hidden" name="coach_class" value={selectedTrip.coach_class} />
            <input type="hidden" name="origin" value={selectedTrip.origin} />
            <input type="hidden" name="destination" value={selectedTrip.destination} />

            <div className="bg-sage/50 rounded-xl p-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-navy-muted">{isTravel ? "Trip" : "Show"}</span>
                <span className="text-navy font-semibold">{selectedTrip.name}</span>
              </div>
              {selectedTrip.origin ? (
                <div className="flex justify-between text-sm">
                  <span className="text-navy-muted">Route</span>
                  <span className="text-navy">
                    {selectedTrip.origin} &rarr; {selectedTrip.destination}
                  </span>
                </div>
              ) : null}
              <div className="flex justify-between text-sm">
                <span className="text-navy-muted">{isTravel ? "Departure" : "Time"}</span>
                <span className="text-navy">{selectedTrip.departure_time}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-navy-muted">{isTravel ? "Class" : "Category"}</span>
                <span className="text-navy">{selectedTrip.coach_class}</span>
              </div>
              <div className="flex justify-between text-sm pt-1 border-t border-sage-mid">
                <span className="text-navy-muted">Price per ticket</span>
                <span className="text-navy font-bold">৳{selectedTrip.price}</span>
              </div>
            </div>

            <div className="bg-sage/50 rounded-xl px-4 py-3 flex items-center justify-between text-sm">
              <span className="text-navy-muted">{isTravel ? "Journey Date" : "Date"}</span>
              <span className="text-navy font-semibold">
                {new Date(`${journeyDate}T00:00:00`).toLocaleDateString("en-GB", {
                  weekday: "short",
                  day: "numeric",
                  month: "short",
                  year: "numeric",
                })}
              </span>
            </div>
            <input type="hidden" name="journey_date" value={journeyDate} />

            {hasSeats ? (
              <>
                <SeatPicker
                  key={selectedTrip.id}
                  category={category}
                  coaches={selectedTrip.coaches ?? []}
                  onSelect={setSeats}
                />
                <input type="hidden" name="passengers" value={passengers} />
              </>
            ) : (
              <Input
                name="passengers"
                label="Number of Tickets"
                type="number"
                min="1"
                placeholder="1"
                value={passengerCount}
                onChange={(e) => setPassengerCount(Math.max(1, Number(e.target.value) || 1))}
              />
            )}

            <div className="bg-sage/50 rounded-xl px-4 py-3 flex items-center justify-between text-sm">
              <span className="text-navy-muted">
                Total ({formatAmount(selectedTrip.price)} × {passengers}{" "}
                {passengers === 1 ? "ticket" : "tickets"})
              </span>
              <span className="text-navy font-bold">{formatAmount(totalAmount)}</span>
            </div>
            <input type="hidden" name="amount" value={totalAmount} />

            <Button
              type="submit"
              loading={bookPending}
              className="w-full h-auto py-4 text-base rounded-xl"
            >
              {bookPending ? "Booking..." : "Confirm Booking"}
            </Button>
          </form>
        )}
      </div>
    </PageTransition>
  );
}
