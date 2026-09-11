"use server";

import { API, token, revalidateLedger } from "./_shared";

export type MerchantPayState = {
  error: string | null;
  success: boolean;
  amount?: string;
  merchant_name?: string;
};

export async function merchantPayAction(
  _prev: MerchantPayState,
  formData: FormData,
): Promise<MerchantPayState> {
  const tok = await token();
  if (!tok) return { error: "Not authenticated.", success: false };

  const merchant_phone = formData.get("merchant_phone") as string;
  const amount = formData.get("amount") as string;
  const note = (formData.get("note") as string) || "";

  try {
    const res = await fetch(`${API}/api/pay/merchant/`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${tok}` },
      body: JSON.stringify({ merchant_phone, amount, note }),
    });
    const data = await res.json();
    if (!res.ok) {
      return { error: firstError(data) || "Payment failed.", success: false };
    }
    revalidateLedger("/pay");
    return {
      error: null,
      success: true,
      amount,
      merchant_name: data.merchant_name ?? merchant_phone,
    };
  } catch {
    return { error: "Could not reach the server.", success: false };
  }
}

function firstError(data: Record<string, unknown>): string {
  if (typeof data.detail === "string" && data.detail) return data.detail;
  const first = Object.values(data)[0];
  if (Array.isArray(first)) return String(first[0] ?? "");
  return "";
}
