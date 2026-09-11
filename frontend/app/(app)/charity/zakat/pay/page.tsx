import { getFoundations } from "@/utils/api";
import { PageHeader } from "@/components/ui/PageHeader";
import { PayZakatForm } from "../PayZakatForm";

export const dynamic = "force-dynamic";

export default async function ZakatPayPage() {
  const foundations = await getFoundations().catch(() => []);
  const foundationList = Array.isArray(foundations) ? foundations : [];

  return (
    <div>
      <PageHeader title="Pay Zakat" subtitle="Charity" showBack backHref="/charity" />
      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl">
        <PayZakatForm foundations={foundationList} />
      </div>
    </div>
  );
}
