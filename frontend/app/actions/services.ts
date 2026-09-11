"use server";

import { cookies } from "next/headers";
import { API, revalidateLedger } from "./_shared";

export type ServiceState = { ok: boolean; message: string };

async function request(
  path: string,
  method: string,
  body?: object,
): Promise<{ ok: boolean; data: Record<string, unknown> }> {
  const token = (await cookies()).get("access_token")?.value;
  if (!token) return { ok: false, data: { detail: "Not authenticated." } };
  try {
    const res = await fetch(`${API}${path}`, {
      method,
      headers: {
        Authorization: `Bearer ${token}`,
        ...(body ? { "Content-Type": "application/json" } : {}),
      },
      ...(body ? { body: JSON.stringify(body) } : {}),
    });
    const data = res.status === 204 ? {} : await res.json().catch(() => ({}));
    return { ok: res.ok, data };
  } catch {
    return { ok: false, data: { detail: "Network error. Try again." } };
  }
}

const fail = (data: Record<string, unknown>, fallback: string): ServiceState => ({
  ok: false,
  message: String(data.detail ?? Object.values(data).flat()[0] ?? fallback),
});

export async function addBankAccountAction(
  _prev: ServiceState,
  form: FormData,
): Promise<ServiceState> {
  const { ok, data } = await request("/api/bank-accounts/", "POST", {
    bank: Number(form.get("bank")),
    account_number: form.get("account_number"),
    account_holder: form.get("account_holder"),
    branch: form.get("branch"),
    routing_number: form.get("routing_number"),
    is_primary: form.get("is_primary") === "on",
  });
  if (!ok) return fail(data, "Could not link account.");
  revalidateLedger("/banking");
  return { ok: true, message: "Bank account linked." };
}
export async function deleteBankAccountAction(id: number): Promise<void> {
  await request(`/api/bank-accounts/${id}/`, "DELETE");
  revalidateLedger("/banking");
}
export async function bankTransferAction(
  _prev: ServiceState,
  form: FormData,
): Promise<ServiceState> {
  const kind = form.get("kind") === "withdraw" ? "withdraw" : "add-money";
  const { ok, data } = await request(`/api/${kind}/`, "POST", {
    bank_account_id: Number(form.get("bank_account_id")),
    amount: Number(form.get("amount")),
  });
  if (!ok) return fail(data, "Transaction failed.");
  revalidateLedger("/banking");
  return {
    ok: true,
    message: kind === "withdraw" ? "Withdrawal completed." : "Money added successfully.",
  };
}
export async function receiveRemittanceAction(
  _prev: ServiceState,
  form: FormData,
): Promise<ServiceState> {
  const { ok, data } = await request("/api/receive-remittance/", "POST", {
    partner_id: Number(form.get("partner_id")),
    sender_name: form.get("sender_name"),
    sender_country: form.get("sender_country"),
    amount_foreign: Number(form.get("amount_foreign")),
  });
  if (!ok) return fail(data, "Could not receive remittance.");
  revalidateLedger("/remittance");
  return { ok: true, message: `Remittance received. ৳${data.amount_bdt} added to your wallet.` };
}
export async function claimOfferAction(id: number): Promise<ServiceState> {
  const { ok, data } = await request(`/api/offers/${id}/claim/`, "POST");
  if (ok) revalidateLedger("/rewards");
  return ok ? { ok: true, message: String(data.message) } : fail(data, "Could not claim offer.");
}
export async function generateStatementAction(
  _prev: ServiceState,
  form: FormData,
): Promise<ServiceState> {
  const { ok, data } = await request("/api/statements/generate/", "POST", {
    year: Number(form.get("year")),
    month: Number(form.get("month")),
  });
  if (!ok) return fail(data, "Could not generate statement.");
  revalidateLedger("/statements");
  return { ok: true, message: "Statement is ready." };
}
export async function createMoneyRequestAction(
  _prev: ServiceState,
  form: FormData,
): Promise<ServiceState> {
  const { ok, data } = await request("/api/money-requests/create/", "POST", {
    phone: form.get("phone"),
    amount: Number(form.get("amount")),
    note: form.get("note"),
  });
  if (!ok) return fail(data, "Could not create request.");
  revalidateLedger("/money-requests");
  return { ok: true, message: "Money request sent." };
}
export async function respondMoneyRequestAction(
  id: number,
  action: "accept" | "decline",
): Promise<ServiceState> {
  const { ok, data } = await request(`/api/money-requests/${id}/respond/`, "POST", { action });
  revalidateLedger("/money-requests");
  return ok
    ? { ok: true, message: `Request ${action === "accept" ? "accepted" : "declined"}.` }
    : fail(data, "Could not respond.");
}
export async function saveNomineeAction(
  _prev: ServiceState,
  form: FormData,
): Promise<ServiceState> {
  const { ok, data } = await request("/api/nominees/", "POST", {
    full_name: form.get("full_name"),
    phone: form.get("phone"),
    nid: form.get("nid"),
    relationship: form.get("relationship"),
    is_primary: form.get("is_primary") === "on",
  });
  if (!ok) return fail(data, "Could not add nominee.");
  revalidateLedger("/account");
  return { ok: true, message: "Nominee added." };
}
export async function deleteNomineeAction(id: number): Promise<void> {
  await request(`/api/nominees/${id}/`, "DELETE");
  revalidateLedger("/account");
}
export async function submitKYCAction(_prev: ServiceState, form: FormData): Promise<ServiceState> {
  const { ok, data } = await request("/api/kyc/", "PUT", {
    document_type: form.get("document_type"),
    document_number: form.get("document_number"),
    date_of_birth: form.get("date_of_birth") || null,
    address: form.get("address"),
  });
  if (!ok) return fail(data, "Could not submit KYC.");
  revalidateLedger("/account");
  return { ok: true, message: "KYC submitted for review." };
}
