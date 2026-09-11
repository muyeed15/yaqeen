"use client";

import { useCallback, useState } from "react";
import { toggleSadaqahJariyahAction } from "@/app/actions";
import { Button } from "@/components/ui/Button";

export function ToggleDonationButton({
  donationId,
  isActive,
}: {
  donationId: number;
  isActive: boolean;
}) {
  const [loading, setLoading] = useState(false);

  const handleToggle = useCallback(async () => {
    setLoading(true);
    try {
      await toggleSadaqahJariyahAction(donationId, !isActive);
    } catch {
      // handled in action
    } finally {
      setLoading(false);
    }
  }, [donationId, isActive]);

  return (
    <Button type="button" variant="secondary" loading={loading} onClick={handleToggle} size="sm">
      {isActive ? "Pause" : "Resume"}
    </Button>
  );
}
