"use client";
import { useActionState } from "react";
import useSWR from "swr";
import { FileText } from "lucide-react";
import { useMutateOnSuccess } from "@/hooks/useMutateOnSuccess";
import { generateStatementAction } from "@/app/actions";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { PageHeader } from "@/components/ui/PageHeader";
import type { AccountStatement, PaginatedResponse } from "@/types";
import { bangladeshNow, formatAmount, formatDate, MONTH_NAMES_LONG } from "@/utils/helpers";
const initial = { ok: false, message: "" };
export default function StatementsPage() {
  const [state, action, pending] = useActionState(generateStatementAction, initial);
  const { data } = useSWR<PaginatedResponse<AccountStatement>>("/api/statements?page=1");
  useMutateOnSuccess(state.ok);
  const now = bangladeshNow();
  const currentMonth = now.getUTCMonth() + 1;
  const currentYear = now.getUTCFullYear();
  return (
    <div>
      <PageHeader title="Statements" subtitle="Monthly Summary" showBack backHref="/dashboard" />
      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl space-y-5">
        <form action={action} className="bg-white border border-sage-mid rounded-2xl p-5">
          <p className="font-semibold text-navy mb-4">Generate a statement</p>
          <div className="grid grid-cols-2 gap-3">
            <Select name="month" label="Month" defaultValue={currentMonth}>
              {MONTH_NAMES_LONG.map((name, i) => (
                <option key={name} value={i + 1}>
                  {name}
                </option>
              ))}
            </Select>
            <Input name="year" label="Year" type="number" defaultValue={currentYear} />
          </div>
          {state.message && (
            <p className={`text-sm mt-3 ${state.ok ? "text-teal" : "text-red-600"}`}>
              {state.message}
            </p>
          )}
          <Button className="w-full mt-4" loading={pending}>
            Generate Statement
          </Button>
        </form>
        <div className="space-y-3">
          {data?.results.map((s) => (
            <div key={s.id} className="bg-white border border-sage-mid rounded-2xl p-5">
              <div className="flex justify-between items-start">
                <div className="flex gap-3">
                  <div className="h-10 w-10 bg-teal/10 rounded-xl grid place-items-center">
                    <FileText className="h-5 w-5 text-teal" />
                  </div>
                  <div>
                    <p className="font-semibold text-navy">{s.period}</p>
                    <p className="text-xs text-navy-muted">
                      {s.transaction_count} transactions · {formatDate(s.generated_at)}
                    </p>
                  </div>
                </div>
                <p className="font-bold text-navy">{formatAmount(s.closing_balance)}</p>
              </div>
              <div className="grid grid-cols-3 gap-3 mt-5 pt-4 border-t border-sage-mid text-xs">
                <div>
                  <p className="text-navy-muted">Opening</p>
                  <p className="font-semibold text-navy">{formatAmount(s.opening_balance)}</p>
                </div>
                <div>
                  <p className="text-navy-muted">Credits</p>
                  <p className="font-semibold text-teal">+{formatAmount(s.total_credits)}</p>
                </div>
                <div>
                  <p className="text-navy-muted">Debits</p>
                  <p className="font-semibold text-navy">-{formatAmount(s.total_debits)}</p>
                </div>
              </div>
            </div>
          ))}
          {!data?.results.length && (
            <p className="bg-white border border-sage-mid rounded-xl py-14 text-center text-sm text-navy-muted">
              No statements generated yet.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
