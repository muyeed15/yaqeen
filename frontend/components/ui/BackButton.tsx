"use client";

import { useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";

type Props = {
  /**
   * Logical parent route. When provided, back always returns to that page so
   * navigation follows the app hierarchy regardless of browser history (new
   * tab, refresh, redirects, or a completed form left in the stack).
   */
  href?: string;
};

export function BackButton({ href }: Props) {
  const router = useRouter();
  return (
    <button
      type="button"
      onClick={() => (href ? router.push(href) : router.back())}
      aria-label="Go back"
      className="text-navy-muted active:opacity-60 transition-opacity"
    >
      <ArrowLeft className="h-5 w-5" aria-hidden="true" />
    </button>
  );
}
