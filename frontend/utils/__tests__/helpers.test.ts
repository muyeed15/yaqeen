import { describe, it, expect } from "vitest";
import {
  calculateTicketTotal,
  formatAmount,
  formatDate,
  formatDuration,
  formatNumber,
  formatRelativeTime,
  getInitials,
  cn,
  STATUS_VARIANT,
  getTxMeta,
} from "../helpers";
import type { Transaction } from "@/types";

describe("formatAmount", () => {
  it("formats a number", () => {
    const result = formatAmount(1234.5);
    expect(result).toBe("৳1,234.50");
  });

  it("formats a string", () => {
    const result = formatAmount("9999.99");
    expect(result).toBe("৳9,999.99");
  });

  it("formats zero", () => {
    expect(formatAmount(0)).toBe("৳0.00");
  });

  it("formats large numbers with South Asian grouping", () => {
    expect(formatAmount(1000000)).toBe("৳10,00,000.00");
    expect(formatAmount(9999999)).toBe("৳99,99,999.00");
    expect(formatAmount(123456789)).toBe("৳12,34,56,789.00");
  });

  it("rounds to two decimal places", () => {
    expect(formatAmount("1234.567")).toBe("৳1,234.57");
  });
});

describe("calculateTicketTotal", () => {
  it("multiplies unit price by passengers", () => {
    expect(calculateTicketTotal("800.00", 2)).toBe(1600);
    expect(calculateTicketTotal(500, 3)).toBe(1500);
  });

  it("rounds to two decimals", () => {
    expect(calculateTicketTotal("33.33", 3)).toBe(99.99);
  });

  it("charges at least one passenger", () => {
    expect(calculateTicketTotal("800.00", 0)).toBe(800);
  });

  it("returns 0 for an invalid price", () => {
    expect(calculateTicketTotal("not-a-number", 2)).toBe(0);
  });
});

describe("formatNumber", () => {
  it("groups integers using South Asian grouping", () => {
    expect(formatNumber(0)).toBe("0");
    expect(formatNumber(999)).toBe("999");
    expect(formatNumber(1000)).toBe("1,000");
    expect(formatNumber(9999999)).toBe("99,99,999");
  });

  it("accepts numeric strings", () => {
    expect(formatNumber("123456")).toBe("1,23,456");
  });
});

describe("formatDate", () => {
  it("formats an ISO date string", () => {
    const result = formatDate("2025-06-15T10:30:00Z");
    expect(result).toBe("15 Jun 2025");
  });

  it("formats another date", () => {
    const result = formatDate("2024-01-01T00:00:00Z");
    expect(result).toBe("01 Jan 2024");
  });
});

describe("formatDuration", () => {
  it("formats months", () => {
    expect(formatDuration(6)).toBe("6 months");
    expect(formatDuration(1)).toBe("1 month");
  });

  it("formats whole years", () => {
    expect(formatDuration(12)).toBe("1 year");
    expect(formatDuration(24)).toBe("2 years");
  });

  it("formats years and months", () => {
    expect(formatDuration(18)).toBe("1 year 6 months");
    expect(formatDuration(30)).toBe("2 years 6 months");
  });

  it("handles zero", () => {
    expect(formatDuration(0)).toBe("0 months");
  });
});

describe("formatRelativeTime", () => {
  it('returns "just now" for recent dates', () => {
    const now = new Date().toISOString();
    expect(formatRelativeTime(now)).toBe("just now");
  });

  it("returns minutes ago", () => {
    const fiveMinAgo = new Date(Date.now() - 5 * 60 * 1000).toISOString();
    expect(formatRelativeTime(fiveMinAgo)).toBe("5m ago");
  });

  it("returns hours ago", () => {
    const threeHoursAgo = new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString();
    expect(formatRelativeTime(threeHoursAgo)).toBe("3h ago");
  });

  it("returns days ago", () => {
    const twoDaysAgo = new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString();
    expect(formatRelativeTime(twoDaysAgo)).toBe("2d ago");
  });
});

describe("getInitials", () => {
  it("returns initials from full name", () => {
    expect(getInitials("John Doe")).toBe("JD");
  });

  it("returns single initial for single name", () => {
    expect(getInitials("Muhammad")).toBe("M");
  });

  it("handles empty string", () => {
    expect(getInitials("")).toBe("");
  });

  it("handles extra spaces", () => {
    expect(getInitials("  Alice   Wonderland  ")).toBe("AW");
  });

  it("limits to two initials", () => {
    expect(getInitials("Alice Bob Carol Dave")).toBe("AB");
  });
});

describe("cn", () => {
  it("merges class names", () => {
    expect(cn("foo", "bar")).toBe("foo bar");
  });

  it("handles conditional classes", () => {
    expect(cn("base", false && "hidden", "visible")).toBe("base visible");
  });

  it("merges tailwind classes correctly", () => {
    expect(cn("px-4", "px-2")).toBe("px-2");
  });
});

describe("STATUS_VARIANT", () => {
  it("maps completed to success", () => {
    expect(STATUS_VARIANT.completed).toBe("success");
  });

  it("maps pending to warning", () => {
    expect(STATUS_VARIANT.pending).toBe("warning");
  });

  it("maps failed to danger", () => {
    expect(STATUS_VARIANT.failed).toBe("danger");
  });

  it("maps reversed to neutral", () => {
    expect(STATUS_VARIANT.reversed).toBe("neutral");
  });
});

describe("getTxMeta", () => {
  const myPhone = "01700000001";

  const makeTx = (overrides: Partial<Transaction> = {}): Transaction => ({
    id: 1,
    reference_id: "ref-001",
    transaction_type: "send",
    sender_phone: "01700000001",
    receiver_phone: "01700000002",
    amount: "500.00",
    fee: "0.00",
    note: "",
    status: "completed",
    merchant_name: null,
    counterparty: "",
    created_at: "2025-06-15T10:30:00Z",
    ...overrides,
  });

  describe("send", () => {
    it("returns correct meta when user is sender", () => {
      const tx = makeTx({ transaction_type: "send", sender_phone: myPhone });
      const meta = getTxMeta(tx, myPhone);
      expect(meta.label).toBe("Send Money");
      expect(meta.minus).toBe(true);
      expect(meta.direction).toBe("to");
      expect(meta.counterparty).toBe("01700000002");
    });

    it("returns correct meta when user is receiver", () => {
      const tx = makeTx({
        transaction_type: "send",
        sender_phone: "01700000002",
        receiver_phone: myPhone,
      });
      const meta = getTxMeta(tx, myPhone);
      expect(meta.label).toBe("Received");
      expect(meta.minus).toBe(false);
      expect(meta.direction).toBe("from");
      expect(meta.counterparty).toBe("01700000002");
    });
  });

  describe("cash_in", () => {
    it("always returns Cash In with Agent counterparty", () => {
      const tx = makeTx({ transaction_type: "cash_in" });
      const meta = getTxMeta(tx, myPhone);
      expect(meta.label).toBe("Cash In");
      expect(meta.color).toBe("text-navy");
      expect(meta.minus).toBe(false);
      expect(meta.counterparty).toBe("Agent");
    });
  });

  describe("cash_out", () => {
    it("always returns Cash Out with Agent counterparty", () => {
      const tx = makeTx({ transaction_type: "cash_out" });
      const meta = getTxMeta(tx, myPhone);
      expect(meta.label).toBe("Cash Out");
      expect(meta.color).toBe("text-navy-muted");
      expect(meta.minus).toBe(true);
      expect(meta.counterparty).toBe("Agent");
    });
  });

  describe("payment", () => {
    it("returns QR Payment when user is sender", () => {
      const tx = makeTx({
        transaction_type: "payment",
        sender_phone: myPhone,
        merchant_name: "Store ABC",
      });
      const meta = getTxMeta(tx, myPhone);
      expect(meta.label).toBe("QR Payment");
      expect(meta.minus).toBe(true);
      expect(meta.counterparty).toBe("Store ABC");
    });

    it("returns Payment Received when user is merchant", () => {
      const tx = makeTx({
        transaction_type: "payment",
        sender_phone: "01700000002",
        receiver_phone: myPhone,
      });
      const meta = getTxMeta(tx, myPhone);
      expect(meta.label).toBe("Payment Received");
      expect(meta.minus).toBe(false);
      expect(meta.counterparty).toBe("01700000002");
    });
  });

  describe("default", () => {
    it("uses transaction_type as label for unknown types", () => {
      const tx = makeTx({ transaction_type: "refund" as never });
      const meta = getTxMeta(tx, myPhone);
      expect(meta.label).toBe("refund");
      expect(meta.color).toBe("text-navy");
    });
  });

  describe("service types", () => {
    it("labels a bill payment as a debit to the counterparty", () => {
      const tx = makeTx({
        transaction_type: "bill",
        sender_phone: myPhone,
        receiver_phone: null,
        counterparty: "DESCO",
      });
      const meta = getTxMeta(tx, myPhone);
      expect(meta.label).toBe("Bill Payment");
      expect(meta.minus).toBe(true);
      expect(meta.counterparty).toBe("DESCO");
    });

    it("labels a remittance credit with the partner name", () => {
      const tx = makeTx({
        transaction_type: "remittance",
        sender_phone: null,
        receiver_phone: myPhone,
        counterparty: "Western Union",
      });
      const meta = getTxMeta(tx, myPhone);
      expect(meta.label).toBe("Remittance");
      expect(meta.minus).toBe(false);
      expect(meta.direction).toBe("from");
      expect(meta.counterparty).toBe("Western Union");
    });
  });
});
