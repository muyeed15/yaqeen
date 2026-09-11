"use client";

import { useState } from "react";
import useSWR from "swr";
import { Users, Search, ChevronDown } from "lucide-react";
import type { Agent } from "@/types";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageTransition } from "@/components/ui/PageTransition";

export default function AgentsPage() {
  const [district, setDistrict] = useState("");
  const params = district ? `&district=${district}` : "";
  const { data } = useSWR<{ results: Agent[] }>(`/api/agents?page=1&page_size=30${params}`);
  const agentList = data?.results ?? [];
  const districts = [...new Set(agentList.map((a) => a.district))].sort();

  return (
    <PageTransition>
      <PageHeader title="Nearby Agents" subtitle="Find" showBack backHref="/dashboard" />
      <div className="px-4 py-5 lg:px-8 lg:py-8 mx-auto max-w-2xl space-y-5">
        <div className="bg-sage/50 border border-sage-mid rounded-2xl p-4">
          <p className="text-xs text-navy-muted leading-relaxed">
            <strong>Cash out</strong>: go to Send Money, enter the agent&apos;s phone number or scan
            their QR. The agent will give you cash.
          </p>
          <p className="text-xs text-navy-muted leading-relaxed mt-2">
            <strong>Cash in</strong>: visit any agent shop. Give cash to the agent and they will
            deposit it into your wallet.
          </p>
        </div>
        {districts.length > 0 && (
          <div className="flex items-center gap-2 bg-white border border-sage-mid rounded-xl px-4 py-3 shadow-sm">
            <Search className="h-4 w-4 text-navy-muted shrink-0" />
            <div className="relative flex-1">
              <select
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
                className="w-full appearance-none bg-transparent pr-6 text-sm text-navy outline-none"
              >
                <option value="">All districts</option>
                {districts.map((d) => (
                  <option key={d} value={d}>
                    {d}
                  </option>
                ))}
              </select>
              <ChevronDown className="pointer-events-none absolute right-0 top-1/2 h-4 w-4 -translate-y-1/2 text-navy-muted" />
            </div>
          </div>
        )}
        {agentList.length === 0 ? (
          <div className="bg-white border border-sage-mid px-6 py-16 text-center rounded-2xl shadow-sm">
            <Users className="h-10 w-10 text-sage-mid mx-auto mb-3" strokeWidth={1.5} />
            <p className="text-navy font-semibold">No agents nearby</p>
            <p className="text-sm text-navy-muted mt-1">Try a different district.</p>
          </div>
        ) : (
          <div className="bg-white border border-sage-mid divide-y divide-sage-mid rounded-2xl overflow-hidden shadow-sm">
            {agentList.map((agent) => (
              <div key={agent.id} className="px-5 py-4 flex items-center gap-3">
                <div className="h-10 w-10 bg-teal/10 flex items-center justify-center shrink-0 rounded-xl">
                  <span className="text-sm font-bold text-teal">{agent.shop_name.charAt(0)}</span>
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-navy">{agent.shop_name}</p>
                  <p className="text-xs text-navy-muted">{agent.address}</p>
                  <p className="text-xs text-navy-muted">
                    {agent.district}, {agent.thana} &middot; {agent.phone}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </PageTransition>
  );
}
