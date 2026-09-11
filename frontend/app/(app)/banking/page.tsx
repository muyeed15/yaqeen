"use client";

import { useActionState, useState } from "react";
import useSWR from "swr";
import { Landmark, Plus, Trash2 } from "lucide-react";
import { addBankAccountAction, bankTransferAction, deleteBankAccountAction } from "@/app/actions";
import { useMutateOnSuccess } from "@/hooks/useMutateOnSuccess";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { PageHeader } from "@/components/ui/PageHeader";
import { Badge } from "@/components/ui/Badge";
import type { Bank, BankAccount, BankTransaction, PaginatedResponse } from "@/types";
import { formatAmount, formatDate } from "@/utils/helpers";

const initial = { ok: false, message: "" };
export default function BankingPage() {
  const [tab, setTab] = useState<"transfer" | "accounts" | "history">("transfer");
  const [mode, setMode] = useState<"add_money" | "withdraw">("add_money");
  const [accountState, accountAction, accountPending] = useActionState(
    addBankAccountAction,
    initial,
  );
  const [txState, txAction, txPending] = useActionState(bankTransferAction, initial);
  const { data: banks } = useSWR<Bank[]>("/api/banks");
  const { data: accountsData, mutate: mutateAccounts } =
    useSWR<BankAccount[]>("/api/bank-accounts");
  const { data: txData } = useSWR<PaginatedResponse<BankTransaction>>(
    "/api/bank-transactions?page=1",
  );
  const accounts = accountsData ?? [];
  useMutateOnSuccess(txState.ok);
  useMutateOnSuccess(accountState.ok);
  return (
    <div>
      <PageHeader
        title="Islamic Banking"
        subtitle="Linked Accounts"
        showBack
        backHref="/dashboard"
      />
      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl space-y-5">
        <div className="grid grid-cols-3 gap-2">
          {(["transfer", "accounts", "history"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`py-2.5 rounded-xl text-sm font-semibold capitalize ${tab === t ? "bg-teal text-white" : "bg-sage text-navy-muted"}`}
            >
              {t}
            </button>
          ))}
        </div>
        {tab === "transfer" && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-2">
              {(["add_money", "withdraw"] as const).map((m) => (
                <button
                  key={m}
                  onClick={() => setMode(m)}
                  className={`p-4 rounded-2xl border text-left ${mode === m ? "border-teal bg-teal/5" : "border-sage-mid bg-white"}`}
                >
                  <Landmark className="h-5 w-5 text-teal mb-2" />
                  <p className="font-semibold text-navy text-sm">
                    {m === "add_money" ? "Add Money" : "Withdraw"}
                  </p>
                  <p className="text-xs text-navy-muted">
                    {m === "add_money" ? "Bank to wallet" : "Wallet to bank"}
                  </p>
                </button>
              ))}
            </div>
            <form
              action={txAction}
              className="bg-white border border-sage-mid rounded-2xl p-5 space-y-4"
            >
              <input type="hidden" name="kind" value={mode} />
              <Select name="bank_account_id" label="Bank Account" required>
                <option value="">Select account</option>
                {accounts.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.bank_name} · {a.masked_account}
                  </option>
                ))}
              </Select>
              <Input name="amount" label="Amount (৳)" type="number" min="1" step="0.01" required />
              {txState.message && (
                <p className={`text-sm ${txState.ok ? "text-teal" : "text-red-600"}`}>
                  {txState.message}
                </p>
              )}
              <Button className="w-full" loading={txPending} disabled={!accounts.length}>
                {mode === "add_money" ? "Add Money" : "Withdraw"}
              </Button>
              {!accounts.length && (
                <p className="text-xs text-center text-navy-muted">Link a bank account first.</p>
              )}
            </form>
          </div>
        )}
        {tab === "accounts" && (
          <div className="space-y-4">
            <form
              action={accountAction}
              className="bg-white border border-sage-mid rounded-2xl p-5 space-y-4"
            >
              <div className="flex items-center gap-2 text-navy font-semibold">
                <Plus className="h-4 w-4" /> Link account
              </div>
              <Select name="bank" label="Islamic Bank" required>
                <option value="">Select bank</option>
                {banks?.map((b) => (
                  <option key={b.id} value={b.id}>
                    {b.name}
                  </option>
                ))}
              </Select>
              <Input name="account_number" label="Account Number" required />
              <Input name="account_holder" label="Account Holder" required />
              <div className="grid grid-cols-2 gap-3">
                <Input name="branch" label="Branch" />
                <Input name="routing_number" label="Routing Number" />
              </div>
              <label className="flex gap-2 text-sm text-navy">
                <input type="checkbox" name="is_primary" /> Set as primary
              </label>
              {accountState.message && (
                <p className={`text-sm ${accountState.ok ? "text-teal" : "text-red-600"}`}>
                  {accountState.message}
                </p>
              )}
              <Button className="w-full" loading={accountPending}>
                Link Account
              </Button>
            </form>
            {accounts.map((a) => (
              <div
                key={a.id}
                className="bg-white border border-sage-mid rounded-xl p-4 flex items-center justify-between"
              >
                <div>
                  <p className="font-semibold text-navy text-sm">{a.bank_name}</p>
                  <p className="text-xs text-navy-muted mt-1">
                    {a.masked_account} · {a.account_holder}
                  </p>
                  <div className="mt-2 flex gap-2">
                    {a.is_primary && <Badge variant="success">Primary</Badge>}
                    <Badge variant={a.is_verified ? "success" : "warning"}>
                      {a.is_verified ? "Verified" : "Pending verification"}
                    </Badge>
                  </div>
                </div>
                <button
                  aria-label="Remove account"
                  onClick={async () => {
                    await deleteBankAccountAction(a.id);
                    await mutateAccounts();
                  }}
                  className="p-2 text-red-500"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        )}
        {tab === "history" && (
          <div className="space-y-3">
            {txData?.results.map((tx) => (
              <div
                key={tx.id}
                className="bg-white border border-sage-mid rounded-xl p-4 flex justify-between"
              >
                <div>
                  <p className="text-sm font-semibold text-navy">
                    {tx.transaction_type === "add_money" ? "Added from bank" : "Withdrawn to bank"}
                  </p>
                  <p className="text-xs text-navy-muted">
                    {tx.bank_name} · {tx.reference} · {formatDate(tx.created_at)}
                  </p>
                </div>
                <p
                  className={`font-bold ${tx.transaction_type === "add_money" ? "text-teal" : "text-navy"}`}
                >
                  {tx.transaction_type === "add_money" ? "+" : "-"}
                  {formatAmount(tx.amount)}
                </p>
              </div>
            ))}
            {!txData?.results.length && <Empty text="No bank transactions yet." />}
          </div>
        )}
      </div>
    </div>
  );
}
function Empty({ text }: { text: string }) {
  return (
    <div className="bg-white border border-sage-mid rounded-2xl py-14 text-center text-sm text-navy-muted">
      {text}
    </div>
  );
}
