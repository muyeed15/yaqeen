"use client";

import { useActionState } from "react";
import { useRouter } from "next/navigation";
import useSWR from "swr";
import { ArrowLeft } from "lucide-react";
import { repayQardHasanAction } from "@/app/actions";
import { useMutateOnSuccess } from "@/hooks/useMutateOnSuccess";
import type { QardHasanApplication } from "@/types";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { PageTransition } from "@/components/ui/PageTransition";

const initialState = { ok: false, message: "" };

const BADGE_COLORS: Record<string, string> = {
  disbursed: "bg-blue-100 text-blue-700",
  repaid: "bg-green-100 text-green-700",
  overdue: "bg-red-100 text-red-700",
  approved: "bg-teal/10 text-teal",
  pending: "bg-yellow-100 text-yellow-700",
  rejected: "bg-gray-100 text-gray-700",
};

export default function MyLoansPage() {
  const router = useRouter();
  const [state, repayAction, repayPending] = useActionState(repayQardHasanAction, initialState);
  useMutateOnSuccess(state.ok);
  const { data } = useSWR<{ results: QardHasanApplication[] }>("/api/loans?page=1");
  const loans = data?.results ?? [];

  return (
    <PageTransition>
      <div className="bg-white px-4 h-16 flex items-center gap-3 border-b border-sage/80">
        <button
          type="button"
          onClick={() => router.push("/loans")}
          aria-label="Go back"
          className="text-navy-muted hover:text-navy active:scale-90 transition-all duration-150"
        >
          <ArrowLeft className="h-5 w-5" aria-hidden="true" />
        </button>
        <div>
          <p className="text-[10px] text-navy-muted font-semibold uppercase tracking-widest leading-none">
            Qard Hasan
          </p>
          <h1 className="text-navy font-bold text-lg leading-tight mt-0.5">My Loans</h1>
        </div>
      </div>

      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl space-y-3">
        {state.message && (
          <div
            className={`rounded-xl px-4 py-3 text-sm font-medium ${
              state.ok
                ? "bg-teal/10 border border-teal/30 text-teal"
                : "border-l-4 border-red-500 bg-red-50 text-red-700"
            }`}
          >
            {state.message}
          </div>
        )}

        {loans.length === 0 ? (
          <div className="bg-white border border-sage-mid px-6 py-16 text-center rounded-2xl shadow-sm">
            <p className="text-navy font-semibold">No Qard Hasan loans</p>
            <p className="text-sm text-navy-muted mt-1">
              Apply for an interest-free loan to get started.
            </p>
          </div>
        ) : (
          loans.map((loan) => (
            <div
              key={loan.id}
              className="bg-white border border-sage-mid rounded-2xl overflow-hidden shadow-sm"
            >
              <div className="p-5">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-semibold text-navy">{loan.product_name}</p>
                  <span
                    className={`text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded ${
                      BADGE_COLORS[loan.status] ?? "bg-gray-100 text-gray-700"
                    }`}
                  >
                    {loan.status}
                  </span>
                </div>
                <p className="text-xs text-navy-muted mt-1">Ref: {loan.loan_reference}</p>
                <div className="flex items-center gap-4 mt-2 text-xs">
                  <span className="text-navy-muted">
                    <span className="text-navy font-semibold">৳{loan.amount_paid}</span> paid
                  </span>
                  <span className="text-navy-muted">
                    of <span className="text-navy font-semibold">৳{loan.amount_due}</span>
                  </span>
                  {Number(loan.hibah_given) > 0 && (
                    <span className="text-teal font-medium">+৳{loan.hibah_given} hibah</span>
                  )}
                </div>
                {loan.due_date && (
                  <p className="text-xs text-navy-muted mt-1">Due: {loan.due_date}</p>
                )}
              </div>
              {loan.status !== "repaid" && (
                <div className="border-t border-sage-mid px-5 py-3 bg-sage/50">
                  <form action={repayAction} className="flex items-end gap-3 flex-wrap">
                    <input type="hidden" name="loan_id" value={loan.id} />
                    <div className="flex-1 min-w-0">
                      <Input
                        name="amount"
                        label="Principal"
                        type="number"
                        placeholder="Amount"
                        required
                      />
                    </div>
                    <div className="w-28 shrink-0">
                      <Input name="hibah" label="Hibah" type="number" placeholder="Optional" />
                    </div>
                    <Button type="submit" loading={repayPending} size="sm">
                      Repay
                    </Button>
                  </form>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </PageTransition>
  );
}
