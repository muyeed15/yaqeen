"use server";

import { redirect } from "next/navigation";
import { API, token, revalidateLedger } from "./_shared";

export async function createMudarabahAccountAction(_prev: unknown, formData: FormData) {
  const t = await token();
  if (!t) redirect("/login");

  const planId = formData.get("plan_id");
  let accountNumber = "";
  try {
    const res = await fetch(`${API}/api/mudarabah/accounts/`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${t}` },
      body: JSON.stringify({ plan_id: Number(planId) }),
    });
    if (res.status === 401) redirect("/login");
    const data = await res.json();
    if (!res.ok) return { error: data.detail ?? "Failed to create account" };
    accountNumber = data.account_number;
  } catch {
    return { error: "Could not reach server." };
  }
  revalidateLedger("/savings", "/savings/accounts", `/savings/accounts/${accountNumber}`);
  redirect(`/savings/accounts/${accountNumber}`);
}

export async function payContributionAction(_prev: unknown, formData: FormData) {
  const t = await token();
  if (!t) redirect("/login");

  try {
    const res = await fetch(`${API}/api/mudarabah/pay/`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${t}` },
      body: JSON.stringify({
        account_number: formData.get("account_number"),
        amount: formData.get("amount"),
      }),
    });
    if (res.status === 401) redirect("/login");
    const data = await res.json();
    if (!res.ok) return { error: data.detail ?? "Payment failed" };
    revalidateLedger(
      "/savings",
      "/savings/accounts",
      `/savings/accounts/${formData.get("account_number")}`,
    );
    return { success: true, message: data.message };
  } catch {
    return { error: "Could not reach server." };
  }
}
