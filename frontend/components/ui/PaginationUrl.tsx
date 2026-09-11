"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Pagination } from "./Pagination";

type Props = {
  page: number;
  totalPages: number;
};

export function PaginationUrl({ page, totalPages }: Props) {
  const router = useRouter();
  const searchParams = useSearchParams();

  const handlePageChange = (p: number) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("page", String(p));
    router.push(`?${params.toString()}`);
  };

  return <Pagination page={page} totalPages={totalPages} onPageChange={handlePageChange} />;
}
