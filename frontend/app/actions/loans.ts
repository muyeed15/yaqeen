"use server";

import { cookies } from "next/headers";
import { API, revalidateLedger } from "./_shared";

export type QardHasanState = { ok: boolean; message: string };

export async function applyQardHasanAction(
  _prev: QardHasanState,
  formData: FormData,
): Promise<QardHasanState> {
  const token = (await cookies()).get("access_token")?.value;
  if (!token) return { ok: false, message: "Not authenticated." };

  const body = JSON.stringify({
    product_id: Number(formData.get("product_id")),
    amount: Number(formData.get("amount")),
  });

  try {
    const res = await fetch(`${API}/api/apply-qard-hasan/`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body,
    });
    const data = await res.json();
    if (!res.ok) return { ok: false, message: data.detail ?? "Application failed." };
    revalidateLedger("/loans", "/loans/my");
    return {
      ok: true,
      message: `Qard Hasan of ৳${data.amount} received. Repay ৳${data.amount_due}. No interest.`,
    };
  } catch {
    return { ok: false, message: "Network error. Try again." };
  }
}

export async function repayQardHasanAction(
  _prev: QardHasanState,
  formData: FormData,
): Promise<QardHasanState> {
  const token = (await cookies()).get("access_token")?.value;
  if (!token) return { ok: false, message: "Not authenticated." };

  const loanId = Number(formData.get("loan_id"));
  const body = JSON.stringify({
    amount: Number(formData.get("amount")),
    hibah: formData.get("hibah") ? Number(formData.get("hibah")) : 0,
  });

  try {
    const res = await fetch(`${API}/api/qard-hasan/${loanId}/repay/`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body,
    });
    const data = await res.json();
    if (!res.ok) return { ok: false, message: data.detail ?? "Repayment failed." };
    revalidateLedger("/loans", "/loans/my");
    if (data.hibah_given > 0) {
      return {
        ok: true,
        message: `Repaid ৳${formData.get("amount")} with ৳${data.hibah_given} hibah. JazakAllah Khair.`,
      };
    }
    return { ok: true, message: `Repaid ৳${formData.get("amount")}.` };
  } catch {
    return { ok: false, message: "Network error. Try again." };
  }
}
