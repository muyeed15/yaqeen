"use client";

import { CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { formatAmount } from "@/utils/helpers";

interface SuccessModalProps {
  amount: string;
  to: string;
  label?: string;
  onClose: () => void;
}

export function SuccessModal({
  amount,
  to,
  label = "Transfer Successful",
  onClose,
}: SuccessModalProps): React.ReactElement {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4 bg-navy/60">
      <div className="bg-white w-full max-w-sm overflow-hidden rounded-xl">
        <div className="bg-teal px-6 py-8 text-center">
          <CheckCircle className="h-14 w-14 text-white mx-auto mb-3" strokeWidth={1.5} />
          <p className="text-white/70 text-xs font-semibold uppercase tracking-widest">{label}</p>
          <p className="text-white text-4xl font-bold tabular-nums mt-2">{formatAmount(amount)}</p>
        </div>

        <div className="divide-y divide-sage-mid">
          <div className="flex px-6 py-3">
            <span className="text-xs font-semibold uppercase tracking-widest text-navy-muted w-28 shrink-0 mt-0.5">
              Paid To
            </span>
            <span className="text-sm font-semibold text-navy">{to}</span>
          </div>
          <div className="flex px-6 py-3">
            <span className="text-xs font-semibold uppercase tracking-widest text-navy-muted w-28 shrink-0 mt-0.5">
              Status
            </span>
            <span className="text-sm font-semibold text-teal">Completed</span>
          </div>
        </div>

        <div className="px-6 py-5">
          <Button variant="primary" size="lg" className="w-full" onClick={onClose}>
            Done
          </Button>
        </div>
      </div>
    </div>
  );
}
