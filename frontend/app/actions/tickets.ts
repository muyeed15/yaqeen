"use server";

import { cookies } from "next/headers";
import { API, revalidateLedger } from "./_shared";

export type TicketState = { ok: boolean; message: string };

export async function bookTicketAction(
  _prev: TicketState,
  formData: FormData,
): Promise<TicketState> {
  const token = (await cookies()).get("access_token")?.value;
  if (!token) return { ok: false, message: "Not authenticated." };

  const body = JSON.stringify({
    provider_id: Number(formData.get("provider_id")),
    trip_id: formData.get("trip_id") ? Number(formData.get("trip_id")) : undefined,
    journey_date: formData.get("journey_date"),
    origin: formData.get("origin"),
    destination: formData.get("destination"),
    departure_time: formData.get("departure_time"),
    trip_name: formData.get("trip_name"),
    coach_class: formData.get("coach_class"),
    coach: formData.get("coach"),
    seat_number: formData.get("seat_number"),
    passengers: Number(formData.get("passengers")) || 1,
    amount: Number(formData.get("amount")),
  });

  try {
    const res = await fetch(`${API}/api/book-ticket/`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body,
    });
    const data = await res.json();
    if (!res.ok) return { ok: false, message: data.detail ?? "Booking failed." };
    revalidateLedger("/tickets");
    return { ok: true, message: `Ticket booked! Ref: ${data.booking_reference}.` };
  } catch {
    return { ok: false, message: "Network error. Try again." };
  }
}

export async function cancelTicketAction(
  _prev: TicketState,
  formData: FormData,
): Promise<TicketState> {
  const token = (await cookies()).get("access_token")?.value;
  if (!token) return { ok: false, message: "Not authenticated." };

  const ticketId = Number(formData.get("ticket_id"));

  try {
    const res = await fetch(`${API}/api/tickets/${ticketId}/cancel/`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    });
    const data = await res.json();
    if (!res.ok) return { ok: false, message: data.detail ?? "Cancel failed." };
    revalidateLedger("/tickets");
    return { ok: true, message: data.message ?? "Ticket cancelled." };
  } catch {
    return { ok: false, message: "Network error. Try again." };
  }
}
