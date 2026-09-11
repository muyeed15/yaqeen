"use client";
import { useActionState, useState } from "react";
import { useMutateOnSuccess } from "@/hooks/useMutateOnSuccess";
import useSWR from "swr";
import { ShieldCheck, Trash2, Users } from "lucide-react";
import { deleteNomineeAction, saveNomineeAction, submitKYCAction } from "@/app/actions";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { PageHeader } from "@/components/ui/PageHeader";
import type { KYCVerification, Nominee } from "@/types";
const initial = { ok: false, message: "" };
export default function AccountPage() {
  const [tab, setTab] = useState<"kyc" | "nominees">("kyc");
  const [kState, kAction, kPending] = useActionState(submitKYCAction, initial);
  const [nState, nAction, nPending] = useActionState(saveNomineeAction, initial);
  const { data: kyc } = useSWR<KYCVerification | null>("/api/kyc");
  const { data: nominees, mutate } = useSWR<Nominee[]>("/api/nominees");
  useMutateOnSuccess(kState.ok);
  useMutateOnSuccess(nState.ok);
  return (
    <div>
      <PageHeader
        title="Account Details"
        subtitle="Identity & Nominees"
        showBack
        backHref="/dashboard"
      />
      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl space-y-5">
        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={() => setTab("kyc")}
            className={`py-2.5 rounded-xl font-semibold text-sm ${tab === "kyc" ? "bg-teal text-white" : "bg-sage text-navy-muted"}`}
          >
            KYC Verification
          </button>
          <button
            onClick={() => setTab("nominees")}
            className={`py-2.5 rounded-xl font-semibold text-sm ${tab === "nominees" ? "bg-teal text-white" : "bg-sage text-navy-muted"}`}
          >
            Nominees
          </button>
        </div>
        {tab === "kyc" && (
          <form
            action={kAction}
            className="bg-white border border-sage-mid rounded-2xl p-5 space-y-4"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 font-semibold text-navy">
                <ShieldCheck className="h-5 w-5 text-teal" /> Identity verification
              </div>
              {kyc && (
                <Badge
                  variant={
                    kyc.status === "verified"
                      ? "success"
                      : kyc.status === "rejected"
                        ? "danger"
                        : "warning"
                  }
                >
                  {kyc.status}
                </Badge>
              )}
            </div>
            <Select
              name="document_type"
              label="Document Type"
              defaultValue={kyc?.document_type ?? "nid"}
            >
              <option value="nid">National ID</option>
              <option value="passport">Passport</option>
              <option value="driving_license">Driving License</option>
            </Select>
            <Input
              name="document_number"
              label="Document Number"
              defaultValue={kyc?.document_number}
              required
            />
            <Input
              name="date_of_birth"
              label="Date of Birth"
              type="date"
              defaultValue={kyc?.date_of_birth ?? ""}
            />
            <label className="block text-[11px] font-semibold uppercase tracking-widest text-navy-muted">
              Address
              <textarea
                name="address"
                defaultValue={kyc?.address}
                rows={3}
                className="mt-2 w-full border border-sage-mid rounded-xl p-3 text-sm resize-none"
              />
            </label>
            {kState.message && (
              <p className={`text-sm ${kState.ok ? "text-teal" : "text-red-600"}`}>
                {kState.message}
              </p>
            )}
            <Button className="w-full" loading={kPending}>
              {kyc ? "Update KYC" : "Submit KYC"}
            </Button>
          </form>
        )}
        {tab === "nominees" && (
          <div className="space-y-4">
            <form
              action={nAction}
              className="bg-white border border-sage-mid rounded-2xl p-5 space-y-4"
            >
              <div className="flex items-center gap-2 font-semibold text-navy">
                <Users className="h-5 w-5 text-teal" /> Add nominee
              </div>
              <Input name="full_name" label="Full Name" required />
              <div className="grid grid-cols-2 gap-3">
                <Input name="phone" label="Phone" required />
                <Input name="nid" label="National ID" />
              </div>
              <Select name="relationship" label="Relationship">
                {["parent", "spouse", "child", "sibling", "other"].map((x) => (
                  <option key={x} value={x} className="capitalize">
                    {x}
                  </option>
                ))}
              </Select>
              <label className="flex gap-2 text-sm text-navy">
                <input name="is_primary" type="checkbox" /> Make primary nominee
              </label>
              {nState.message && (
                <p className={`text-sm ${nState.ok ? "text-teal" : "text-red-600"}`}>
                  {nState.message}
                </p>
              )}
              <Button className="w-full" loading={nPending}>
                Add Nominee
              </Button>
            </form>
            {nominees?.map((n) => (
              <div
                key={n.id}
                className="bg-white border border-sage-mid rounded-xl p-4 flex justify-between"
              >
                <div>
                  <div className="flex gap-2">
                    <p className="font-semibold text-sm text-navy">{n.full_name}</p>
                    {n.is_primary && <Badge variant="success">Primary</Badge>}
                  </div>
                  <p className="text-xs text-navy-muted mt-1">
                    {n.relationship} · {n.phone}
                    {n.nid ? ` · NID ${n.nid}` : ""}
                  </p>
                </div>
                <button
                  onClick={async () => {
                    await deleteNomineeAction(n.id);
                    await mutate();
                  }}
                  className="text-red-500 p-2"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
