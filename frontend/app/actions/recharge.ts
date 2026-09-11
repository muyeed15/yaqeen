"use server";

import { cookies } from "next/headers";
import { API, revalidateLedger } from "./_shared";

export type RechargeState = { ok: boolean; message: string };

export async function rechargeAction(
  _prev: RechargeState,
  formData: FormData,
): Promise<RechargeState> {
  const token = (await cookies()).get("access_token")?.value;
  if (!token) return { ok: false, message: "Not authenticated." };

  const body = JSON.stringify({
    operator_id: Number(formData.get("operator_id")),
    phone_number: formData.get("phone_number"),
    amount: Number(formData.get("amount")),
    recharge_type: formData.get("recharge_type"),
    data_pack_id: formData.get("data_pack_id") ? Number(formData.get("data_pack_id")) : undefined,
  });

  try {
    const res = await fetch(`${API}/api/recharge/`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body,
    });
    const data = await res.json();
    if (!res.ok) return { ok: false, message: data.detail ?? "Recharge failed." };
    revalidateLedger("/recharge");
    return { ok: true, message: `Successfully recharged ৳${data.amount}.` };
  } catch {
    return { ok: false, message: "Network error. Try again." };
  }
}
