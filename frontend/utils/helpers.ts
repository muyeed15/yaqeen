import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import type { Transaction } from "./api";

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

export const STATUS_VARIANT: Record<string, "success" | "warning" | "danger" | "neutral"> = {
  completed: "success",
  pending: "warning",
  failed: "danger",
  reversed: "neutral",
};

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export const MONTH_NAMES_LONG = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

// Bangladesh has used a fixed UTC+6 offset with no daylight saving since 2010.
const BD_OFFSET_MS = 6 * 60 * 60 * 1000;

/**
 * Current time shifted to the Asia/Dhaka (UTC+6) wall clock. Read it with the
 * UTC getters so the server and client render the same date regardless of the
 * runtime's own timezone.
 */
export function bangladeshNow(): Date {
  return new Date(Date.now() + BD_OFFSET_MS);
}

// South Asian (lakh/crore) digit grouping: last three digits, then pairs.
// Implemented manually so server and client render identically regardless of
// the runtime's ICU locale data (Node and browsers disagree on `en-BD`).
function groupSouthAsian(whole: string): string {
  if (whole.length <= 3) return whole;
  const lastThree = whole.slice(-3);
  const rest = whole.slice(0, -3);
  return `${rest.replace(/\B(?=(\d{2})+(?!\d))/g, ",")},${lastThree}`;
}

export function formatNumber(value: string | number): string {
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (!Number.isFinite(num)) return "0";
  const sign = num < 0 ? "-" : "";
  return `${sign}${groupSouthAsian(Math.trunc(Math.abs(num)).toString())}`;
}

export function formatAmount(amount: string | number): string {
  const num = typeof amount === "string" ? parseFloat(amount) : amount;
  if (!Number.isFinite(num)) return "৳0.00";
  const sign = num < 0 ? "-" : "";
  const [whole, fraction] = Math.abs(num).toFixed(2).split(".");
  return `${sign}৳${groupSouthAsian(whole)}.${fraction}`;
}

/**
 * Ticket total = unit price × passenger count, rounded to two decimals. At
 * least one passenger is always charged.
 */
export function calculateTicketTotal(unitPrice: string | number, passengers: number): number {
  const price = typeof unitPrice === "string" ? parseFloat(unitPrice) : unitPrice;
  const count = Math.max(1, Math.trunc(passengers) || 1);
  if (!Number.isFinite(price)) return 0;
  return Math.round(price * count * 100) / 100;
}

export function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  if (Number.isNaN(date.getTime())) return "";
  const bd = new Date(date.getTime() + BD_OFFSET_MS);
  const day = String(bd.getUTCDate()).padStart(2, "0");
  return `${day} ${MONTHS[bd.getUTCMonth()]} ${bd.getUTCFullYear()}`;
}

export function formatDuration(months: number): string {
  if (months <= 0) return "0 months";
  const years = Math.floor(months / 12);
  const rem = months % 12;
  if (years === 0) return `${rem} month${rem === 1 ? "" : "s"}`;
  const yearPart = `${years} year${years === 1 ? "" : "s"}`;
  if (rem === 0) return yearPart;
  return `${yearPart} ${rem} month${rem === 1 ? "" : "s"}`;
}

export function formatRelativeTime(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  return `${days}d ago`;
}

export function getInitials(name: string): string {
  return name
    .split(" ")
    .filter(Boolean)
    .map((w) => w[0].toUpperCase())
    .join("")
    .slice(0, 2);
}

type TxMeta = {
  label: string;
  color: string;
  minus: boolean;
  direction: "to" | "from";
  counterparty: string;
};

const SERVICE_LABELS: Record<string, string> = {
  bill: "Bill Payment",
  recharge: "Mobile Recharge",
  bank: "Bank Transfer",
  savings: "Savings",
  charity: "Charity",
  loan: "Qard Hasan",
  ticket: "Ticket Booking",
  remittance: "Remittance",
  gateway: "Gateway Payment",
};

export function getTxMeta(tx: Transaction, myPhone: string): TxMeta {
  const isSender = tx.sender_phone === myPhone;

  switch (tx.transaction_type) {
    case "send":
      return {
        label: isSender ? "Send Money" : "Received",
        color: isSender ? "text-navy-muted" : "text-navy",
        minus: isSender,
        direction: isSender ? "to" : "from",
        counterparty: isSender ? (tx.receiver_phone ?? "-") : (tx.sender_phone ?? "-"),
      };
    case "cash_in":
      return {
        label: "Cash In",
        color: "text-navy",
        minus: false,
        direction: "from",
        counterparty: tx.counterparty || "Agent",
      };
    case "cash_out":
      return {
        label: "Cash Out",
        color: "text-navy-muted",
        minus: true,
        direction: "to",
        counterparty: tx.counterparty || "Agent",
      };
    case "payment":
      return {
        label: isSender ? "QR Payment" : "Payment Received",
        color: isSender ? "text-navy-muted" : "text-navy",
        minus: isSender,
        direction: isSender ? "to" : "from",
        // Payer sees the merchant name; merchant sees the payer's phone.
        counterparty: isSender
          ? (tx.merchant_name ?? tx.receiver_phone ?? "-")
          : (tx.sender_phone ?? "-"),
      };
    default: {
      const serviceLabel = SERVICE_LABELS[tx.transaction_type];
      return {
        label: serviceLabel ?? tx.transaction_type,
        color: serviceLabel ? (isSender ? "text-navy-muted" : "text-navy") : "text-navy",
        minus: isSender,
        direction: isSender ? "to" : "from",
        counterparty: tx.counterparty || (isSender ? tx.receiver_phone : tx.sender_phone) || "-",
      };
    }
  }
}
