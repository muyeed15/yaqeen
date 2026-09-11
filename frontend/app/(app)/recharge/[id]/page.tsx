"use client";

import { useActionState, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import useSWR from "swr";
import { ArrowLeft, Info } from "lucide-react";
import { rechargeAction } from "@/app/actions";
import type { Operator, DataPack } from "@/types";
import { EntityLogo } from "@/components/ui/EntityLogo";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { PageTransition } from "@/components/ui/PageTransition";

const RECHARGE_TYPES = [
  { value: "prepaid", label: "Prepaid" },
  { value: "postpaid", label: "Postpaid" },
  { value: "data_pack", label: "Data Pack" },
];

const initialState = { ok: false, message: "" };

export default function RechargeOperatorPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [state, formAction, pending] = useActionState(rechargeAction, initialState);
  const [rechargeType, setRechargeType] = useState("prepaid");

  const { data } = useSWR<Operator[]>("/api/operators");
  const operator = (data ?? []).find((op) => op.id === Number(id)) ?? null;
  const { data: packs } = useSWR<DataPack[]>(
    rechargeType === "data_pack" ? `/api/data-packs?operator_id=${id}` : null,
  );
  const dataPacks = packs ?? [];

  return (
    <PageTransition>
      <div className="bg-white px-4 h-16 flex items-center gap-3 border-b border-sage/80">
        <button
          type="button"
          onClick={() => router.push("/recharge")}
          aria-label="Go back"
          className="text-navy-muted hover:text-navy active:scale-90 transition-all duration-150"
        >
          <ArrowLeft className="h-5 w-5" aria-hidden="true" />
        </button>
        <div>
          <p className="text-[10px] text-navy-muted font-semibold uppercase tracking-widest leading-none">
            Mobile Recharge
          </p>
          <h1 className="text-navy font-bold text-lg leading-tight mt-0.5">
            {operator?.name ?? "Recharge"}
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
              Instant recharge. Amount is deducted from your wallet.
            </p>
          </div>

          {operator && (
            <div className="bg-sage/50 rounded-xl px-4 py-3 flex items-center gap-3">
              <EntityLogo logo={operator.logo} name={operator.name} />
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-widest text-navy-muted">
                  Operator
                </p>
                <p className="text-sm font-semibold text-navy">{operator.name}</p>
              </div>
            </div>
          )}

          <input type="hidden" name="operator_id" value={id} />

          <Input
            name="phone_number"
            label="Phone Number"
            type="text"
            inputMode="numeric"
            placeholder="01XXXXXXXXX"
            required
          />

          <div>
            <p className="text-[11px] font-semibold uppercase tracking-widest text-navy-muted mb-2">
              Recharge Type
            </p>
            <div className="flex gap-2">
              {RECHARGE_TYPES.map((t) => (
                <button
                  key={t.value}
                  type="button"
                  onClick={() => setRechargeType(t.value)}
                  className={`flex-1 py-2.5 rounded-xl text-xs font-semibold transition-all duration-150 active:scale-95 ${
                    rechargeType === t.value
                      ? "bg-teal text-white shadow-sm"
                      : "bg-sage text-navy-muted hover:bg-sage-mid/20"
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>
            <input type="hidden" name="recharge_type" value={rechargeType} />
          </div>

          {rechargeType === "data_pack" && dataPacks.length > 0 && (
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-widest text-navy-muted mb-2">
                Data Pack
              </p>
              <div className="space-y-2">
                {dataPacks.map((p) => (
                  <label
                    key={p.id}
                    className="flex items-center gap-3 border border-sage-mid rounded-xl p-3 cursor-pointer hover:border-teal/50 has-[:checked]:border-teal has-[:checked]:bg-teal/5 transition-all duration-150"
                  >
                    <input
                      type="radio"
                      name="data_pack_id"
                      value={p.id}
                      className="accent-teal"
                      required
                    />
                    <div>
                      <p className="text-sm font-semibold text-navy">
                        {p.name} ({p.volume})
                      </p>
                      <p className="text-xs text-navy-muted">
                        ৳{p.amount} / {p.validity_days}d
                      </p>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          )}

          {rechargeType !== "data_pack" && (
            <Input name="amount" label="Amount (৳)" type="number" placeholder="100" required />
          )}

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
            {pending ? "Recharging..." : "Recharge Now"}
          </Button>
        </form>
      </div>
    </PageTransition>
  );
}
