"use client";

import { useActionState } from "react";
import { updateHawlAction } from "@/app/actions";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";

export function UpdateHawlForm() {
  const [state, action, pending] = useActionState(updateHawlAction, null);

  return (
    <div className="bg-white border border-sage-mid p-5 rounded-xl">
      <h2 className="text-navy font-semibold text-sm mb-4">Update Wealth</h2>
      {state?.success && (
        <div className="mb-4 bg-teal/10 border border-teal/20 px-4 py-3 text-sm text-navy">
          Hawl tracking updated.
        </div>
      )}
      {state?.error && (
        <div className="mb-4 border-l-4 border-red-500 bg-red-50 px-4 py-3 text-sm text-red-700">
          {state.error}
        </div>
      )}
      <form action={action} className="space-y-4">
        <Input
          label="Current Wealth (৳)"
          name="current_wealth"
          type="number"
          step="0.01"
          min="0"
          placeholder="e.g. 500000"
        />
        <Button type="submit" variant="primary" loading={pending} className="w-full">
          {pending ? "Updating..." : "Update Hawl"}
        </Button>
      </form>
    </div>
  );
}
