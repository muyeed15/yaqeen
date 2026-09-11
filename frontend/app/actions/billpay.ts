"use server";

import { cookies } from "next/headers";
import { API, revalidateLedger } from "./_shared";

export type BillPayState = { ok: boolean; message: string };

export async function payBillAction(
  _prev: BillPayState,
  formData: FormData,
): Promise<BillPayState> {
  const token = (await cookies()).get("access_token")?.value;
  if (!token) return { ok: false, message: "Not authenticated." };

  const body = JSON.stringify({
    biller_id: Number(formData.get("biller_id")),
    account_number: formData.get("account_number"),
    bill_number: formData.get("bill_number") ?? "",
    amount: Number(formData.get("amount")),
    bill_month: formData.get("bill_month") ?? "",
  });

  try {
    const res = await fetch(`${API}/api/pay-bill/`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body,
    });
    const data = await res.json();
    if (!res.ok) return { ok: false, message: data.detail ?? "Bill payment failed." };
    revalidateLedger("/billpay");
    return { ok: true, message: `Bill of ৳${data.amount} paid successfully.` };
  } catch {
    return { ok: false, message: "Network error. Try again." };
  }
}
