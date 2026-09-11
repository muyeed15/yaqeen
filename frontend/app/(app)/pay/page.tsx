"use client";

import { useActionState, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Store, Info, QrCode } from "lucide-react";
import { merchantPayAction } from "@/app/actions";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageTransition } from "@/components/ui/PageTransition";
import { SuccessModal } from "@/components/ui/SuccessModal";
import { QRScanner } from "@/components/ui/QRScanner";
import { usePhoneLookup } from "@/hooks/usePhoneLookup";
import { formatAmount } from "@/utils/helpers";

const initialState = { error: null, success: false };

export default function PayPage() {
  const [state, formAction] = useActionState(merchantPayAction, initialState);
  const router = useRouter();
  const searchParams = useSearchParams();
  const formRef = useRef<HTMLFormElement>(null);
  const submitRef = useRef<HTMLButtonElement>(null);
  const [showScanner, setShowScanner] = useState(false);
  const [merchantPhone, setMerchantPhone] = useState(searchParams.get("phone") ?? "");
  const [confirmData, setConfirmData] = useState<{
    phone: string;
    amount: string;
    note: string;
  } | null>(null);
  const { lookup } = usePhoneLookup(merchantPhone);

  const showSuccess = state.success && !!state.amount && !!state.merchant_name;

  const handleConfirm = () => {
    const form = formRef.current;
    if (!form) return;
    const data = new FormData(form);
    const phone = data.get("merchant_phone") as string;
    const amount = data.get("amount") as string;
    if (!phone || !amount) return;
    setConfirmData({
      phone,
      amount,
      note: (data.get("note") as string) || "",
    });
  };

  return (
    <div>
      {showScanner && (
        <QRScanner
          onScan={(phone) => {
            setMerchantPhone(phone);
            setShowScanner(false);
          }}
          onClose={() => setShowScanner(false)}
        />
      )}

      {showSuccess && (
        <SuccessModal
          amount={state.amount!}
          to={state.merchant_name!}
          label="Payment Successful"
          onClose={() => router.replace("/dashboard")}
        />
      )}

      <PageTransition>
        <PageHeader title="Pay Merchant" subtitle="QR Payment" showBack backHref="/dashboard" />

        <div className="px-4 py-5 lg:px-8 lg:py-8 max-w-2xl mx-auto">
          {state.error && (
            <div className="border-l-4 border-red-500 bg-red-50 px-4 py-3 text-sm text-red-700 rounded-r mb-5">
              {state.error}
            </div>
          )}

          <form
            ref={formRef}
            action={formAction}
            className="bg-white border border-sage-mid rounded-2xl p-5 shadow-sm"
          >
            <button ref={submitRef} type="submit" className="hidden" />
            <div className="text-navy-muted pb-4 flex gap-2 items-start">
              <Info className="h-4 w-4 mt-0.5 shrink-0 text-navy-muted" />
              <p className="text-xs leading-snug">
                Payments are instant and <strong>cannot be reversed</strong>. Verify the merchant
                phone number before paying.
              </p>
            </div>
            <div>
              <div className="py-4">
                <div className="flex items-end gap-2">
                  <div className="flex-1">
                    <Input
                      label="Merchant Phone Number"
                      name="merchant_phone"
                      type="tel"
                      required
                      placeholder="01XXXXXXXXX"
                      autoComplete="off"
                      value={merchantPhone}
                      onChange={(e) => setMerchantPhone(e.target.value)}
                    />
                  </div>
                  <button
                    type="button"
                    onClick={() => setShowScanner(true)}
                    className="h-[42px] w-[42px] mb-0.5 flex items-center justify-center border border-sage-mid bg-white text-navy-muted hover:bg-sage active:scale-95 shrink-0 rounded-xl transition-all duration-150"
                    aria-label="Scan QR code"
                  >
                    <QrCode className="h-5 w-5" />
                  </button>
                </div>
              </div>
              <div className="py-4">
                <Input
                  label="Amount (৳)"
                  name="amount"
                  type="number"
                  step="0.01"
                  min="1"
                  required
                  placeholder="0.00"
                />
                <p className="text-xs text-navy-muted mt-2 flex items-center gap-1">
                  <Info className="h-3 w-3" /> A small fee may apply for this payment.
                </p>
              </div>
              <div className="py-4">
                <Input
                  label="Note (Optional)"
                  name="note"
                  type="text"
                  placeholder="e.g. Table 4, order #12…"
                />
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={() => router.push("/dashboard")}
                className="flex-1 py-4 text-sm font-semibold text-navy bg-sage active:scale-[0.98] rounded-xl transition-all duration-150"
              >
                Cancel
              </button>
              <Button
                type="button"
                variant="primary"
                onClick={handleConfirm}
                className="flex-1 h-auto py-4 text-base rounded-xl"
              >
                Confirm
              </Button>
            </div>
          </form>
        </div>
      </PageTransition>

      {confirmData && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center px-4 bg-navy/60 backdrop-blur-sm"
          onClick={() => setConfirmData(null)}
        >
          <div
            className="bg-white w-full max-w-sm rounded-2xl overflow-hidden shadow-xl animate-scale-in"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6 space-y-4">
              <div className="text-center">
                <div className="mx-auto h-12 w-12 bg-teal/10 rounded-full flex items-center justify-center mb-3">
                  <Store className="h-6 w-6 text-teal" />
                </div>
                <p className="text-navy font-bold text-base">Confirm Payment</p>
                <p className="text-xs text-navy-muted mt-1">Are you sure you want to pay?</p>
              </div>
              <div className="bg-sage rounded-xl px-4 py-3 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-navy-muted">To</span>
                  <span className="text-navy font-semibold">
                    {lookup?.full_name ?? confirmData.phone}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-navy-muted">Amount</span>
                  <span className="text-navy font-bold">{formatAmount(confirmData.amount)}</span>
                </div>
                {confirmData.note && (
                  <div className="flex justify-between text-sm">
                    <span className="text-navy-muted">Note</span>
                    <span className="text-navy">{confirmData.note}</span>
                  </div>
                )}
              </div>
            </div>
            <div className="flex border-t border-sage-mid">
              <button
                type="button"
                onClick={() => setConfirmData(null)}
                className="flex-1 py-4 text-sm font-semibold text-navy-muted border-r border-sage-mid hover:bg-sage active:opacity-70 transition-all duration-150"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => {
                  setConfirmData(null);
                  submitRef.current?.click();
                }}
                className="flex-1 py-4 text-sm font-semibold text-teal hover:bg-teal/5 active:opacity-70 transition-all duration-150"
              >
                Pay
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
