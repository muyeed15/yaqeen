"use client";
import { useActionState } from "react";
import useSWR from "swr";
import { Globe2 } from "lucide-react";
import { useMutateOnSuccess } from "@/hooks/useMutateOnSuccess";
import { receiveRemittanceAction } from "@/app/actions";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { PageHeader } from "@/components/ui/PageHeader";
import { Select } from "@/components/ui/Select";
import type { PaginatedResponse, RemittancePartner, RemittanceTransaction } from "@/types";
import { formatAmount, formatDate } from "@/utils/helpers";
const initial = { ok: false, message: "" };
export default function RemittancePage() {
  const [state, action, pending] = useActionState(receiveRemittanceAction, initial);
  const { data: partners } = useSWR<RemittancePartner[]>("/api/remittance-partners");
  const { data: history } =
    useSWR<PaginatedResponse<RemittanceTransaction>>("/api/remittances?page=1");
  useMutateOnSuccess(state.ok);
  return (
    <div>
      <PageHeader title="Remittance" subtitle="Hawala" showBack backHref="/dashboard" />
      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl space-y-5">
        <form action={action} className="bg-white border border-sage-mid rounded-2xl p-5 space-y-4">
          <div className="flex gap-3">
            <div className="h-10 w-10 rounded-xl bg-teal/10 grid place-items-center">
              <Globe2 className="h-5 w-5 text-teal" />
            </div>
            <div>
              <p className="font-semibold text-navy">Receive international money</p>
              <p className="text-xs text-navy-muted">Funds are converted and credited instantly.</p>
            </div>
          </div>
          <Select name="partner_id" label="Partner" required>
            <option value="">Select partner</option>
            {partners?.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} · {p.country} ({p.currency} 1 = ৳{p.exchange_rate})
              </option>
            ))}
          </Select>
          <div className="grid sm:grid-cols-2 gap-3">
            <Input name="sender_name" label="Sender Name" required />
            <Input name="sender_country" label="Sender Country" required />
          </div>
          <Input
            name="amount_foreign"
            label="Foreign Amount"
            type="number"
            min="0.01"
            step="0.01"
            required
          />
          {state.message && (
            <p className={`text-sm ${state.ok ? "text-teal" : "text-red-600"}`}>{state.message}</p>
          )}
          <Button className="w-full" loading={pending}>
            Receive Remittance
          </Button>
        </form>
        <div>
          <h2 className="font-semibold text-navy mb-3">Recent remittances</h2>
          <div className="space-y-3">
            {history?.results.map((r) => (
              <div
                key={r.id}
                className="bg-white border border-sage-mid rounded-xl p-4 flex justify-between"
              >
                <div>
                  <p className="text-sm font-semibold text-navy">{r.sender_name}</p>
                  <p className="text-xs text-navy-muted">
                    {r.partner_name} · {r.amount_foreign} foreign · {formatDate(r.created_at)}
                  </p>
                </div>
                <p className="font-bold text-teal">+{formatAmount(r.amount_bdt)}</p>
              </div>
            ))}
            {!history?.results.length && (
              <p className="bg-white border border-sage-mid rounded-xl py-12 text-center text-sm text-navy-muted">
                No remittances yet.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
