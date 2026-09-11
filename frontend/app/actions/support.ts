"use server";

import { revalidatePath } from "next/cache";
import { cookies } from "next/headers";
import { API } from "./_shared";

export type SupportState = { ok: boolean; message: string };

export async function createTicketAction(
  _prev: SupportState,
  formData: FormData,
): Promise<SupportState> {
  const token = (await cookies()).get("access_token")?.value;
  if (!token) return { ok: false, message: "Not authenticated." };

  const body = JSON.stringify({
    subject: formData.get("subject"),
    category: formData.get("category") ?? "general",
    message: formData.get("message"),
  });

  try {
    const res = await fetch(`${API}/api/support-tickets/`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body,
    });
    const data = await res.json();
    if (!res.ok) return { ok: false, message: data.detail ?? "Failed to create ticket." };
    revalidatePath("/support");
    return { ok: true, message: `Ticket #${data.id} created.` };
  } catch {
    return { ok: false, message: "Network error. Try again." };
  }
}

export async function sendMessageAction(
  _prev: SupportState,
  formData: FormData,
): Promise<SupportState> {
  const token = (await cookies()).get("access_token")?.value;
  if (!token) return { ok: false, message: "Not authenticated." };

  const ticketId = Number(formData.get("ticket_id"));
  const body = JSON.stringify({ message: formData.get("message") });

  try {
    const res = await fetch(`${API}/api/support-tickets/${ticketId}/reply/`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body,
    });
    const data = await res.json();
    if (!res.ok) return { ok: false, message: data.detail ?? "Failed to send message." };
    revalidatePath("/support");
    return { ok: true, message: "Message sent." };
  } catch {
    return { ok: false, message: "Network error. Try again." };
  }
}
