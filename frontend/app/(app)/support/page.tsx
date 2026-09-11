"use client";

import { useActionState, useState } from "react";
import useSWR from "swr";
import { Info } from "lucide-react";
import { createTicketAction, sendMessageAction } from "@/app/actions";
import { useMutateOnSuccess } from "@/hooks/useMutateOnSuccess";
import type { SupportCategory, SupportTicket } from "@/types";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Button } from "@/components/ui/Button";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageTransition } from "@/components/ui/PageTransition";

const initTicket = { ok: false, message: "" };
const initMsg = { ok: false, message: "" };
const BADGE_COLORS: Record<string, string> = {
  open: "bg-yellow-100 text-yellow-700",
  in_progress: "bg-blue-100 text-blue-700",
  resolved: "bg-green-100 text-green-700",
  closed: "bg-gray-100 text-gray-700",
};

export default function SupportPage() {
  const [tab, setTab] = useState<"new" | "list">("new");
  const [tState, tAction, tPending] = useActionState(createTicketAction, initTicket);
  const [mState, mAction, mPending] = useActionState(sendMessageAction, initMsg);
  useMutateOnSuccess(tState.ok);
  useMutateOnSuccess(mState.ok);
  const { data: tickets } = useSWR<SupportTicket[]>("/api/support-tickets");
  const { data: categoryData } = useSWR<SupportCategory[]>("/api/support-categories");
  const ticketList = tickets ?? [];
  const categories = categoryData ?? [];
  const [selectedTicket, setSelectedTicket] = useState<SupportTicket | null>(null);
  if (tState.ok && tab !== "list") setTab("list");

  return (
    <PageTransition>
      <PageHeader title="Help & Support" subtitle="Contact Us" showBack backHref="/dashboard" />
      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl space-y-5">
        <div className="flex gap-2">
          {(["new", "list"] as const).map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setTab(t)}
              className={`flex-1 py-2.5 rounded-xl text-sm font-semibold transition-all duration-150 active:scale-95 ${
                tab === t
                  ? "bg-teal text-white shadow-sm"
                  : "bg-sage text-navy-muted hover:bg-sage-mid/20"
              }`}
            >
              {t === "new"
                ? "New Ticket"
                : `My Tickets${ticketList.length > 0 ? ` (${ticketList.length})` : ""}`}
            </button>
          ))}
        </div>
        {tab === "new" && (
          <form
            action={tAction}
            className="bg-white border border-sage-mid rounded-2xl p-5 shadow-sm space-y-5"
          >
            <div className="flex gap-2 items-start">
              <Info className="h-4 w-4 mt-0.5 shrink-0 text-navy-muted" />
              <p className="text-xs leading-snug text-navy-muted">
                Our support team typically responds within 24 hours.
              </p>
            </div>
            <Input
              name="subject"
              label="Subject"
              type="text"
              placeholder="Brief description of your issue"
              required
            />
            <Select name="category" label="Category">
              <option value="">Select category</option>
              {categories.map((c) => (
                <option key={c.key} value={c.key}>
                  {c.label}
                </option>
              ))}
            </Select>
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-widest text-navy-muted mb-2">
                Message
              </p>
              <textarea
                name="message"
                rows={4}
                placeholder="Describe your issue in detail..."
                className="w-full border border-sage-mid rounded-xl px-3.5 py-3 text-sm text-navy bg-white focus:outline-none focus:ring-2 focus:ring-teal/10 focus:border-teal transition-all duration-150 resize-none"
                required
              />
            </div>
            {tState.message && !tState.ok && (
              <div className="border-l-4 border-red-500 bg-red-50 px-4 py-3 text-sm text-red-700 rounded-r">
                {tState.message}
              </div>
            )}
            <Button
              type="submit"
              loading={tPending}
              className="w-full h-auto py-4 text-base rounded-xl"
            >
              {tPending ? "Submitting..." : "Submit Ticket"}
            </Button>
          </form>
        )}
        {tab === "list" && (
          <div className="space-y-3">
            {ticketList.length === 0 ? (
              <div className="bg-white border border-sage-mid px-6 py-16 text-center rounded-2xl shadow-sm">
                <p className="text-navy font-semibold">No tickets yet</p>
                <p className="text-sm text-navy-muted mt-1">Create a new ticket to get help.</p>
              </div>
            ) : (
              ticketList.map((ticket) => {
                const isOpen = selectedTicket?.id === ticket.id;
                return (
                  <div
                    key={ticket.id}
                    className="bg-white border border-sage-mid rounded-2xl overflow-hidden shadow-sm"
                  >
                    <button
                      type="button"
                      onClick={() => setSelectedTicket(isOpen ? null : ticket)}
                      className="w-full p-5 text-left"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <p className="text-sm font-semibold text-navy">
                              #{ticket.id} {ticket.subject}
                            </p>
                            <span
                              className={`text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded shrink-0 ${BADGE_COLORS[ticket.status] ?? "bg-gray-100 text-gray-700"}`}
                            >
                              {ticket.status.replace("_", " ")}
                            </span>
                          </div>
                          <p className="text-xs text-navy-muted mt-1">
                            {ticket.category_label || ticket.category} &middot; {ticket.created_at}
                          </p>
                        </div>
                      </div>
                    </button>
                    {isOpen && (
                      <div className="border-t border-sage-mid px-5 py-4 bg-sage/30">
                        {ticket.messages?.length > 0 && (
                          <div className="space-y-3 mb-4">
                            {ticket.messages.map((msg) => (
                              <div
                                key={msg.id}
                                className={`text-sm leading-relaxed ${msg.is_staff_reply ? "text-navy" : "text-navy-muted"}`}
                              >
                                <span className="text-[10px] font-semibold uppercase tracking-widest text-navy-muted block">
                                  {msg.sender_phone} {msg.is_staff_reply ? "(Staff)" : ""}
                                </span>
                                {msg.message}
                              </div>
                            ))}
                          </div>
                        )}
                        {ticket.status !== "closed" && ticket.status !== "resolved" && (
                          <form action={mAction} className="flex gap-2">
                            <input type="hidden" name="ticket_id" value={ticket.id} />
                            <Input
                              name="message"
                              placeholder="Type your reply..."
                              className="flex-1"
                            />
                            <Button type="submit" loading={mPending} size="sm" className="shrink-0">
                              Send
                            </Button>
                          </form>
                        )}
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        )}
      </div>
    </PageTransition>
  );
}
