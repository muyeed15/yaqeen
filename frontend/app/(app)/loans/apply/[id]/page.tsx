"use client";

import { useActionState } from "react";
import { useParams, useRouter } from "next/navigation";
import useSWR from "swr";
import { ArrowLeft, Info } from "lucide-react";
import { applyQardHasanAction } from "@/app/actions";
import type { QardHasanProduct } from "@/types";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { PageTransition } from "@/components/ui/PageTransition";

const initialState = { ok: false, message: "" };

export default function ApplyLoanPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [state, formAction, pending] = useActionState(applyQardHasanAction, initialState);

  const { data } = useSWR<QardHasanProduct[]>("/api/loan-products");
  const product = (data ?? []).find((p) => p.id === Number(id)) ?? null;

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
          <h1 className="text-navy font-bold text-lg leading-tight mt-0.5">
            {product?.name ?? "Apply"}
          </h1>
        </div>
      </div>

      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl space-y-5">
        {state.ok && (
          <div className="bg-teal/10 border border-teal/30 rounded-xl px-4 py-3 text-sm font-medium text-teal">
            {state.message}
          </div>
        )}

        {product && (
          <form
            action={formAction}
            className="bg-white border border-sage-mid rounded-2xl p-5 shadow-sm space-y-5"
          >
            <div className="flex gap-2 items-start">
              <Info className="h-4 w-4 mt-0.5 shrink-0 text-navy-muted" />
              <p className="text-xs leading-snug text-navy-muted">
                Qard Hasan is an interest-free benevolent loan. The full amount is credited to your
                wallet immediately; you repay the principal only.
              </p>
            </div>

            <div className="bg-sage/50 rounded-xl p-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-navy-muted">Plan</span>
                <span className="text-navy font-semibold">{product.name}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-navy-muted">Range</span>
                <span className="text-navy">
                  {product.min_amount} &ndash; {product.max_amount} ৳
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-navy-muted">Tenure</span>
                <span className="text-navy">{product.tenure_days} days</span>
              </div>
              <div className="flex justify-between text-sm pt-1 border-t border-sage-mid">
                <span className="text-navy-muted">Service fee</span>
                <span className="text-navy font-bold">{product.service_fee} ৳</span>
              </div>
            </div>

            <input type="hidden" name="product_id" value={id} />

            <Input
              name="amount"
              label="Amount (৳)"
              type="number"
              placeholder={`${product.min_amount} - ${product.max_amount}`}
              required
            />
            <p className="text-xs text-navy-muted">
              Enter an amount between {product.min_amount} ৳ and {product.max_amount} ৳.
            </p>

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
              {pending ? "Applying..." : "Apply for Qard Hasan"}
            </Button>
          </form>
        )}

        {state.ok && (
          <Button
            type="button"
            variant="secondary"
            onClick={() => router.push("/loans/my")}
            className="w-full"
          >
            View My Loans
          </Button>
        )}
      </div>
    </PageTransition>
  );
}
