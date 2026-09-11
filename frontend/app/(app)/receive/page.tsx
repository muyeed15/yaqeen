import { getMe, getQRCode } from "@/utils/api";
import { Card } from "@/components/ui/Card";
import { PageHeader } from "@/components/ui/PageHeader";
import Image from "next/image";

export const dynamic = "force-dynamic";

export default async function ReceivePage() {
  const [user, qrDataUrl] = await Promise.all([getMe(), getQRCode()]);

  return (
    <div>
      <PageHeader title="Receive" subtitle="My QR" showBack backHref="/dashboard" />
      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl">
        <Card className="p-8 w-full">
          <div className="flex flex-col items-center">
            {qrDataUrl ? (
              <Image src={qrDataUrl} alt="Your QR Code" width={224} height={224} unoptimized />
            ) : (
              <div className="h-56 w-56 bg-sage flex items-center justify-center text-navy-muted text-sm">
                Could not load QR code.
              </div>
            )}
            <p className="text-sm text-navy-muted text-center mt-6">
              Ask the sender to scan this QR code to send money to
            </p>
            <p className="text-lg font-bold text-navy text-center mt-1">{user.phone}</p>
          </div>
        </Card>
      </div>
    </div>
  );
}
