"use client";

import { useActionState } from "react";
import { useParams, useRouter } from "next/navigation";
import useSWR from "swr";
import { ArrowLeft, Info } from "lucide-react";
import { payBillAction } from "@/app/actions";
import type { Biller } from "@/types";
import { EntityLogo } from "@/components/ui/EntityLogo";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { PageTransition } from "@/components/ui/PageTransition";

const initialState = { ok: false, message: "" };

export default function PayBillPage() {
  const { billerId, category } = useParams<{
    billerId: string;
    category: string;
  }>();
  const router = useRouter();
  const [state, formAction, pending] = useActionState(payBillAction, initialState);

  const { data } = useSWR<Biller[]>(`/api/billers?category=${encodeURIComponent(category)}`);
  const biller = (data ?? []).find((b) => b.id === Number(billerId)) ?? null;

  return (
    <PageTransition>
      <div className="bg-white px-4 h-16 flex items-center gap-3 border-b border-sage/80">
        <button
          type="button"
          onClick={() => router.push(`/billpay/${category}`)}
          aria-label="Go back"
          className="text-navy-muted hover:text-navy active:scale-90 transition-all duration-150"
        >
          <ArrowLeft className="h-5 w-5" aria-hidden="true" />
        </button>
        <div>
          <p className="text-[10px] text-navy-muted font-semibold uppercase tracking-widest leading-none">
            Pay Bills
          </p>
          <h1 className="text-navy font-bold text-lg leading-tight mt-0.5">
            {biller?.name ?? "Pay Bill"}
          </h1>
        </div>
      </div>

      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl space-y-5">
        {state.ok && (
          <div className="bg-teal/10 border border-teal/30 rounded-xl px-4 py-3 text-sm font-medium text-teal">
            {state.message}
          </div>
        )}

        <form
          action={formAction}
          className="bg-white border border-sage-mid rounded-2xl p-5 shadow-sm space-y-5"
        >
          <div className="flex gap-2 items-start">
            <Info className="h-4 w-4 mt-0.5 shrink-0 text-navy-muted" />
            <p className="text-xs leading-snug text-navy-muted">
              Bill payment is instant. Amount is deducted from your wallet.
            </p>
          </div>

          {biller && (
            <div className="bg-sage/50 rounded-xl px-4 py-3 flex items-center gap-3">
              <EntityLogo logo={biller.logo} name={biller.name} />
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-widest text-navy-muted">
                  Biller
                </p>
                <p className="text-sm font-semibold text-navy">{biller.name}</p>
              </div>
            </div>
          )}

          <input type="hidden" name="biller_id" value={billerId} />

          <Input
            name="account_number"
            label={biller?.account_no_label ?? "Account Number"}
            type="text"
            placeholder="Enter account number"
            required
          />
          <Input
            name="bill_number"
            label="Bill Number"
            type="text"
            placeholder="Enter bill number"
            required
          />
          <Input
            name="amount"
            label={biller?.amount_no_label ?? "Amount (৳)"}
            type="number"
            placeholder="500"
            required
          />
          <Input name="bill_month" label="Bill Month" type="month" />

          {state.message && !state.ok && (
            <div className="border-l-4 border-red-500 bg-red-50 px-4 py-3 text-sm text-red-700 rounded-r">
              {state.message}
            </div>
          )}

          <Button
            type="submit"
            loading={pending}
            className="w-full h-auto py-4 text-base rounded-xl"
          >
            {pending ? "Processing..." : "Pay Bill"}
          </Button>
        </form>
      </div>
    </PageTransition>
  );
}
