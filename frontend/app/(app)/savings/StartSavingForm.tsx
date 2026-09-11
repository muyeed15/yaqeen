"use client";

import { useActionState } from "react";
import { createMudarabahAccountAction } from "@/app/actions";
import { Button } from "@/components/ui/Button";

export function StartSavingForm({ planId }: { planId: number }) {
  const [state, action, pending] = useActionState(createMudarabahAccountAction, null);

  return (
    <form action={action}>
      <input type="hidden" name="plan_id" value={planId} />
      {state?.error && <p className="text-xs text-red-600 mb-2">{state.error}</p>}
      <Button
        type="submit"
        loading={pending}
        className="w-full py-2 text-sm font-semibold rounded-lg"
      >
        {pending ? "Starting..." : "Start Saving"}
      </Button>
    </form>
  );
}
