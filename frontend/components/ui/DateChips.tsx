"use client";

import { useMemo, useState } from "react";

type Chip = {
  weekday: string;
  day: string;
  month: string;
  iso: string;
};

function toIso(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(
    d.getDate(),
  ).padStart(2, "0")}`;
}

function formatChip(d: Date): Chip {
  return {
    weekday: d.toLocaleDateString("en-US", { weekday: "short" }),
    day: String(d.getDate()),
    month: d.toLocaleDateString("en-US", { month: "short" }),
    iso: toIso(d),
  };
}

type Props = {
  label?: string;
  days?: number;
  defaultOffset?: number;
  onSelect: (isoDate: string) => void;
};

export function DateChips({ label = "Select Date", days = 7, defaultOffset = 3, onSelect }: Props) {
  const dates = useMemo(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return Array.from({ length: days }, (_, i) => {
      const d = new Date(today);
      d.setDate(today.getDate() + i);
      return formatChip(d);
    });
  }, [days]);

  const [selected, setSelected] = useState<string>(
    dates[defaultOffset]?.iso ?? dates[0]?.iso ?? "",
  );

  function pick(iso: string) {
    setSelected(iso);
    onSelect(iso);
  }

  return (
    <div>
      <p className="text-[11px] font-semibold uppercase tracking-widest text-navy-muted mb-2">
        {label}
      </p>
      <div className="flex gap-1.5 overflow-x-auto pb-1 -mx-1 px-1">
        {dates.map((d) => (
          <button
            key={d.iso}
            type="button"
            onClick={() => pick(d.iso)}
            className={`flex flex-col items-center min-w-14 px-3 py-2 rounded-xl border transition-all duration-150 active:scale-95 shrink-0 ${
              selected === d.iso
                ? "bg-teal border-teal text-white shadow-sm"
                : "bg-white border-sage-mid text-navy hover:border-teal"
            }`}
          >
            <span className="text-[9px] font-semibold uppercase tracking-wide">{d.weekday}</span>
            <span className="text-base font-bold leading-tight">{d.day}</span>
            <span className="text-[10px]">{d.month}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
