import { PageHeader } from "@/components/ui/PageHeader";
import { CalculateZakatForm } from "./CalculateZakatForm";

export const dynamic = "force-dynamic";

export default async function ZakatCalculatePage() {
  return (
    <div>
      <PageHeader title="Calculate Zakat" subtitle="Charity" showBack backHref="/charity" />
      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl">
        <CalculateZakatForm />
      </div>
    </div>
  );
}
