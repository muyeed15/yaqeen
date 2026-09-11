"use client";

import { useMemo, useState } from "react";
import { Check, Users } from "lucide-react";

type Props = {
  category: string;
  maxSelect?: number;
  coaches?: string[];
  onSelect: (seats: string[]) => void;
};

type Layout = {
  cols: number;
  rows: number;
  labels: string[];
  aisleAfter?: number;
};

const LAYOUTS: Record<string, Layout> = {
  bus: { cols: 4, rows: 10, labels: ["A", "B", "C", "D"], aisleAfter: 2 },
  train: { cols: 5, rows: 12, labels: ["A", "B", "C", "D", "E"], aisleAfter: 2 },
  airline: { cols: 6, rows: 8, labels: ["A", "B", "C", "D", "E", "F"], aisleAfter: 3 },
  cinema: { cols: 8, rows: 15, labels: ["A", "B", "C", "D", "E", "F", "G", "H"], aisleAfter: 4 },
  ferry: { cols: 3, rows: 8, labels: ["A", "B", "C"], aisleAfter: 1 },
  event: { cols: 5, rows: 6, labels: ["A", "B", "C", "D", "E"] },
};

function hashString(s: string) {
  let h = 0;
  for (let i = 0; i < s.length; i++) {
    h = (Math.imul(31, h) + s.charCodeAt(i)) | 0;
  }
  return h >>> 0;
}

function seededRandom(seed: number) {
  let s = seed >>> 0;
  return () => {
    s = (Math.imul(s, 1664525) + 1013904223) >>> 0;
    return s / 4294967296;
  };
}

function generateBooked(
  cols: number,
  rows: number,
  labels: string[],
  coach: string,
  baseSeed: number,
) {
  const rand = seededRandom((hashString(coach) ^ baseSeed) >>> 0);
  const booked = new Set<string>();
  const toBook = Math.floor(cols * rows * 0.3);
  while (booked.size < toBook) {
    const r = Math.floor(rand() * rows);
    const c = Math.floor(rand() * cols);
    booked.add(coach ? `${coach} ${r + 1}${labels[c]}` : `${labels[c]}${r + 1}`);
  }
  return booked;
}

export default function SeatPicker({ category, maxSelect = 9, coaches = [], onSelect }: Props) {
  const layout = LAYOUTS[category] ?? LAYOUTS.bus;
  const hasCoaches = coaches.length > 0;
  const [seed] = useState(() => Math.floor(Math.random() * 2 ** 32));
  const [selectedCoach, setSelectedCoach] = useState(coaches[0] ?? "");
  const [selected, setSelected] = useState<Set<string>>(new Set());

  const booked = useMemo(
    () => generateBooked(layout.cols, layout.rows, layout.labels, selectedCoach, seed),
    [layout, selectedCoach, seed],
  );

  const seats = useMemo(() => {
    const list: { label: string; row: number; col: number; booked: boolean }[] = [];
    for (let r = 0; r < layout.rows; r++) {
      for (let c = 0; c < layout.cols; c++) {
        const id = seatId(r + 1, c);
        list.push({
          label: layout.labels[c],
          row: r + 1,
          col: c,
          booked: booked.has(id),
        });
      }
    }
    return list;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [layout, booked, selectedCoach, hasCoaches]);

  const totalCols = layout.cols + 1 + (layout.aisleAfter ? 1 : 0);
  const selectedList = Array.from(selected);
  const atMax = selectedList.length >= maxSelect;
  const selectedCoaches = hasCoaches ? [...new Set(selectedList.map((s) => s.split(" ")[0]))] : [];

  function seatId(row: number, col: number) {
    return hasCoaches
      ? `${selectedCoach} ${row}${layout.labels[col]}`
      : `${layout.labels[col]}${row}`;
  }

  function shortLabel(row: number, col: number) {
    return `${row}${layout.labels[col]}`;
  }

  function toggleSeat(seatId: string) {
    const next = new Set(selected);
    if (next.has(seatId)) {
      next.delete(seatId);
    } else {
      if (next.size >= maxSelect) return;
      next.add(seatId);
    }
    setSelected(next);
    onSelect(Array.from(next));
  }

  function selectCoach(coach: string) {
    setSelectedCoach(coach);
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between gap-2">
        <p className="text-[11px] font-semibold uppercase tracking-widest text-navy-muted">
          {hasCoaches ? `Select Coach & Seats` : "Select Seats"}
        </p>
        <span
          className={`flex items-center gap-1 text-xs font-semibold ${
            atMax ? "text-amber-600" : "text-teal"
          }`}
        >
          <Users className="h-3.5 w-3.5" />
          {selectedList.length > 0 ? `${selectedList.length} selected` : "Tap seats to select"}
        </span>
      </div>

      {atMax && (
        <p className="text-[10px] text-amber-600">Maximum {maxSelect} seats per booking.</p>
      )}

      {hasCoaches && (
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-widest text-navy-muted mb-1.5">
            Coach
          </p>
          <div className="flex flex-wrap gap-1.5">
            {coaches.map((c) => (
              <button
                key={c}
                type="button"
                onClick={() => selectCoach(c)}
                className={`min-w-9 px-2.5 py-1.5 rounded-lg text-sm font-bold transition-all duration-150 active:scale-95 ${
                  selectedCoach === c
                    ? "bg-teal text-white shadow-sm"
                    : "bg-white border border-sage-mid text-navy hover:border-teal"
                }`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="flex justify-center">
        <div
          className="grid gap-1 sm:gap-1.5 p-3 bg-sage/50 rounded-2xl w-full max-w-xs"
          style={{ gridTemplateColumns: `repeat(${totalCols}, minmax(0, 1fr))` }}
        >
          {/* Header row */}
          <div className="aspect-square" />
          {Array.from({ length: layout.cols }).map((_, ci) => (
            <div key={`h-${ci}`} className="contents">
              {layout.aisleAfter === ci ? <div className="aspect-square" /> : null}
              <div className="aspect-square flex items-center justify-center">
                <span className="text-[9px] font-semibold text-navy-muted">
                  {layout.labels[ci]}
                </span>
              </div>
            </div>
          ))}

          {/* Seat rows */}
          {Array.from({ length: layout.rows }).map((_, ri) => {
            const rowNum = ri + 1;
            const cells: React.ReactNode[] = [
              <div key={`rn-${rowNum}`} className="aspect-square flex items-center justify-center">
                <span className="text-[9px] font-semibold text-navy-muted">{rowNum}</span>
              </div>,
            ];
            for (let ci = 0; ci < layout.cols; ci++) {
              if (layout.aisleAfter === ci) {
                cells.push(<div key={`aisle-${rowNum}-${ci}`} className="aspect-square" />);
              }
              const id = seatId(rowNum, ci);
              const seat = seats.find((s) => s.row === rowNum && s.col === ci);
              const isBooked = seat?.booked ?? false;
              const isSelected = selected.has(id);
              cells.push(
                <button
                  key={id}
                  type="button"
                  disabled={isBooked}
                  onClick={() => toggleSeat(id)}
                  title={
                    isBooked
                      ? `${id} - Booked`
                      : isSelected
                        ? `${id} - Selected`
                        : `${id} - Available`
                  }
                  className={`aspect-square w-full rounded-md flex items-center justify-center text-[8px] sm:text-[9px] font-bold transition-all duration-100
                    ${isBooked ? "bg-sage-mid/40 text-sage-mid cursor-not-allowed" : ""}
                    ${isSelected ? "bg-teal text-white ring-2 ring-teal/30 scale-105" : ""}
                    ${
                      !isBooked && !isSelected
                        ? "bg-white border border-sage-mid hover:border-teal hover:bg-teal/5 text-navy-muted cursor-pointer"
                        : ""
                    }
                  `}
                >
                  {isSelected ? <Check className="h-3 w-3" /> : shortLabel(rowNum, ci)}
                </button>,
              );
            }
            return (
              <div key={`row-${rowNum}`} className="contents">
                {cells}
              </div>
            );
          })}

          {/* Legend */}
          <div className="col-span-full flex items-center justify-center gap-4 mt-3 pt-3 border-t border-sage-mid">
            <span className="flex items-center gap-1.5 text-[9px] text-navy-muted">
              <span className="w-3 h-3 rounded bg-white border border-sage-mid" />
              Available
            </span>
            <span className="flex items-center gap-1.5 text-[9px] text-navy-muted">
              <span className="w-3 h-3 rounded bg-teal" />
              Selected
            </span>
            <span className="flex items-center gap-1.5 text-[9px] text-navy-muted">
              <span className="w-3 h-3 rounded bg-sage-mid/40" />
              Booked
            </span>
          </div>
        </div>
      </div>

      {selectedList.length > 0 && (
        <div className="bg-white border border-teal rounded-xl px-4 py-2.5 flex items-center justify-between gap-2">
          <span className="text-sm font-bold text-navy truncate">{selectedList.join(", ")}</span>
          <span className="text-[10px] font-semibold uppercase tracking-widest text-teal shrink-0">
            {selectedList.length} {selectedList.length === 1 ? "seat" : "seats"}
          </span>
        </div>
      )}

      <input type="hidden" name="seat_number" value={selectedList.join(", ")} />
      {hasCoaches && (
        <input type="hidden" name="coach" value={selectedCoaches.join(", ") || selectedCoach} />
      )}
    </div>
  );
}
