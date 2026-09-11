"use client";

type Props = {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
};

function getPages(page: number, total: number): (number | "...")[] {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);

  const left = Math.max(2, page - 1);
  const right = Math.min(total - 1, page + 1);
  const pages: (number | "...")[] = [1];

  if (left > 2) pages.push("...");
  for (let i = left; i <= right; i++) pages.push(i);
  if (right < total - 1) pages.push("...");
  pages.push(total);

  return pages;
}

export function Pagination({ page, totalPages, onPageChange }: Props) {
  if (totalPages <= 1) return null;

  return (
    <div className="flex items-center justify-center gap-1 mt-4">
      <button
        type="button"
        onClick={() => onPageChange(page - 1)}
        disabled={page === 1}
        className="px-3 h-8 text-xs font-semibold border border-sage-mid text-navy bg-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors rounded-lg"
      >
        ← Prev
      </button>

      {getPages(page, totalPages).map((p, i) =>
        p === "..." ? (
          <span
            key={`dots-${i}`}
            className="w-8 h-8 flex items-center justify-center text-xs text-navy-muted"
          >
            …
          </span>
        ) : (
          <button
            key={p}
            type="button"
            onClick={() => onPageChange(p)}
            className={`w-8 h-8 text-xs font-semibold border transition-colors rounded-lg ${
              p === page ? "bg-teal text-white border-teal" : "bg-white border-sage-mid text-navy"
            }`}
          >
            {p}
          </button>
        ),
      )}

      <button
        type="button"
        onClick={() => onPageChange(page + 1)}
        disabled={page === totalPages}
        className="px-3 h-8 text-xs font-semibold border border-sage-mid text-navy bg-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors rounded-lg"
      >
        Next →
      </button>
    </div>
  );
}
