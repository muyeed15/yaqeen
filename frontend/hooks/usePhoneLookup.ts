"use client";

import { useEffect, useState } from "react";
import useSWR from "swr";
import type { PhoneLookup } from "@/types";

function useDebounced(value: string, delay = 400) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

export function usePhoneLookup(phone: string) {
  const debounced = useDebounced(phone.trim(), 400);
  const key = debounced.length >= 11 ? `/api/lookup/${encodeURIComponent(debounced)}` : null;
  const { data, error } = useSWR<PhoneLookup>(key);

  return {
    lookup: key && !error ? (data ?? null) : null,
    loading: !!key && !data && !error,
    notFound: !!key && !!error,
  };
}
