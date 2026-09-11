import { getHawl } from "@/utils/api";
import { formatDate } from "@/utils/helpers";
import { PageHeader } from "@/components/ui/PageHeader";
import { UpdateHawlForm } from "./UpdateHawlForm";
import { RenewHawlButton } from "./RenewHawlButton";

export const dynamic = "force-dynamic";

export default async function HawlPage() {
  const hawl = await getHawl().catch(() => null);

  return (
    <div>
      <PageHeader title="Hawl Tracking" subtitle="Charity" showBack backHref="/charity" />
      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl">
        <div className="space-y-6">
          <div className="bg-white border border-sage-mid p-5 rounded-xl">
            <h2 className="text-navy font-semibold text-sm mb-4">Current Status</h2>
            {hawl ? (
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-navy-muted">Zakat Eligible</span>
                  <span className={hawl.is_eligible ? "text-navy font-medium" : "text-navy-muted"}>
                    {hawl.is_eligible ? "Yes" : "No"}
                  </span>
                </div>
                {hawl.nisab_crossed_at && (
                  <div className="flex justify-between">
                    <span className="text-navy-muted">Nisab Crossed</span>
                    <span className="text-navy">{formatDate(hawl.nisab_crossed_at)}</span>
                  </div>
                )}
                {hawl.next_hawl_date && (
                  <div className="flex justify-between">
                    <span className="text-navy-muted">Next Hawl Date</span>
                    <span className="text-navy">{formatDate(hawl.next_hawl_date)}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-navy-muted">Last Updated</span>
                  <span className="text-navy">{formatDate(hawl.updated_at)}</span>
                </div>
              </div>
            ) : (
              <p className="text-sm text-navy-muted">
                No hawl tracking record yet. Update your wealth below.
              </p>
            )}
          </div>

          <UpdateHawlForm />

          {hawl?.is_eligible && (
            <div className="bg-white border border-sage-mid p-5 rounded-xl">
              <h2 className="text-navy font-semibold text-sm mb-3">Renew Hawl Period</h2>
              <p className="text-xs text-navy-muted mb-3">
                Start a new hawl period after paying zakat. This resets the tracking cycle.
              </p>
              <RenewHawlButton />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
