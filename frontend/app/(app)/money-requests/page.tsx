"use client";
import { useActionState, useState } from "react";
import useSWR from "swr";
import { createMoneyRequestAction, respondMoneyRequestAction } from "@/app/actions";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { PageHeader } from "@/components/ui/PageHeader";
import type { MoneyRequest, PaginatedResponse, User } from "@/types";
import { formatAmount, formatDate } from "@/utils/helpers";
const initial = { ok: false, message: "" };
export default function MoneyRequestsPage() {
  const [state, action, pending] = useActionState(createMoneyRequestAction, initial);
  const { data, mutate } = useSWR<PaginatedResponse<MoneyRequest>>("/api/money-requests?page=1");
  const { data: me } = useSWR<User>("/api/me");
  const [msg, setMsg] = useState("");
  return (
    <div>
      <PageHeader
        title="Money Requests"
        subtitle="Request & Respond"
        showBack
        backHref="/dashboard"
      />
      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl space-y-5">
        <form action={action} className="bg-white border border-sage-mid rounded-2xl p-5 space-y-4">
          <p className="font-semibold text-navy">Request money</p>
          <Input name="phone" label="From Phone Number" placeholder="01XXXXXXXXX" required />
          <Input name="amount" label="Amount (৳)" type="number" min="1" step="0.01" required />
          <Input name="note" label="Note" placeholder="What is this for?" />
          {state.message && (
            <p className={`text-sm ${state.ok ? "text-teal" : "text-red-600"}`}>{state.message}</p>
          )}
          <Button className="w-full" loading={pending}>
            Send Request
          </Button>
        </form>
        {msg && <p className="bg-teal/10 text-teal rounded-xl px-4 py-3 text-sm">{msg}</p>}
        <div className="space-y-3">
          {data?.results.map((r) => {
            const incoming = r.target_phone === me?.phone;
            return (
              <div key={r.id} className="bg-white border border-sage-mid rounded-2xl p-5">
                <div className="flex justify-between">
                  <div>
                    <p className="font-semibold text-navy">
                      {incoming ? `From ${r.requester_phone}` : `To ${r.target_phone}`}
                    </p>
                    <p className="text-xs text-navy-muted mt-1">
                      {r.note || "Money request"} · {formatDate(r.created_at)}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-navy">{formatAmount(r.amount)}</p>
                    <Badge
                      variant={
                        r.status === "accepted"
                          ? "success"
                          : r.status === "pending"
                            ? "warning"
                            : "neutral"
                      }
                    >
                      {r.status}
                    </Badge>
                  </div>
                </div>
                {incoming && r.status === "pending" && (
                  <div className="grid grid-cols-2 gap-2 mt-4">
                    <Button
                      size="sm"
                      onClick={async () => {
                        const x = await respondMoneyRequestAction(r.id, "accept");
                        setMsg(x.message);
                        await mutate();
                      }}
                    >
                      Accept
                    </Button>
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={async () => {
                        const x = await respondMoneyRequestAction(r.id, "decline");
                        setMsg(x.message);
                        await mutate();
                      }}
                    >
                      Decline
                    </Button>
                  </div>
                )}
              </div>
            );
          })}
          {!data?.results.length && (
            <p className="bg-white border border-sage-mid rounded-xl py-14 text-center text-sm text-navy-muted">
              No money requests yet.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
