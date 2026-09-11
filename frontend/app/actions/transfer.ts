"use server";

import { API, token, revalidateLedger } from "./_shared";

export type TransferState = {
  error: string | null;
  success: boolean;
  amount?: string;
  receiver_phone?: string;
};

export async function transferAction(
  _prev: TransferState,
  formData: FormData,
): Promise<TransferState> {
  const tok = await token();
  if (!tok) return { error: "Not authenticated.", success: false };

  const receiver_phone = formData.get("receiver_phone") as string;
  const amount = formData.get("amount") as string;
  const note = (formData.get("note") as string) || "";

  try {
    const res = await fetch(`${API}/api/transfer/`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${tok}` },
      body: JSON.stringify({ receiver_phone, amount, note }),
    });
    const data = await res.json();
    if (!res.ok) return { error: data.detail ?? "Transfer failed.", success: false };
    revalidateLedger("/send");
    return { error: null, success: true, amount, receiver_phone };
  } catch {
    return { error: "Could not reach the server.", success: false };
  }
}
