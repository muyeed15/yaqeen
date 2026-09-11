"use client";

import { useActionState } from "react";
import { renewHawlAction } from "@/app/actions";
import { Button } from "@/components/ui/Button";

export function RenewHawlButton() {
  const [state, action, pending] = useActionState(renewHawlAction, null);

  return (
    <form action={action}>
      {state && !("error" in state) && (
        <div className="mb-3 bg-teal/10 border border-teal/20 px-4 py-3 text-sm text-navy">
          Hawl renewed.
        </div>
      )}
      {state && "error" in state && (
        <div className="mb-3 border-l-4 border-red-500 bg-red-50 px-4 py-3 text-sm text-red-700">
          {state.error}
        </div>
      )}
      <Button type="submit" variant="secondary" loading={pending}>
        {pending ? "Renewing..." : "Renew Hawl"}
      </Button>
    </form>
  );
}
