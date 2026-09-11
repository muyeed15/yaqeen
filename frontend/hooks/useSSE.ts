"use client";

import { useEffect, useRef } from "react";
import { mutate } from "swr";
import type { Notification } from "@/types";
import { logger } from "@/utils/logger";

type SSENotification = Pick<Notification, "id" | "message" | "is_read" | "created_at">;

export function useSSE(initialLastId: number, onNotification: (n: SSENotification) => void) {
  const lastIdRef = useRef(initialLastId);
  const onNotificationRef = useRef(onNotification);

  useEffect(() => {
    onNotificationRef.current = onNotification;
  });

  useEffect(() => {
    let es: EventSource | null = null;
    let active = true;
    let retryTimeout: ReturnType<typeof setTimeout> | null = null;

    function connect() {
      if (!active) return;

      es = new EventSource(`/api/notifications/stream?last_id=${lastIdRef.current}`);

      es.addEventListener("notification", (e: MessageEvent) => {
        const data: SSENotification = JSON.parse(e.data);
        lastIdRef.current = Math.max(lastIdRef.current, data.id);
        onNotificationRef.current(data);
        // A mutation that produced this notification may have changed any of the
        // user's collections (wallet, ledger, history lists, rewards, …).
        void mutate((key) => typeof key === "string" && key.startsWith("/api/"));
      });

      es.onerror = (ev: Event) => {
        logger.error("useSSE", "SSE connection error, reconnecting in 3s", ev);
        es?.close();
        es = null;
        if (active) retryTimeout = setTimeout(connect, 3000);
      };
    }

    connect();

    return () => {
      active = false;
      if (retryTimeout) clearTimeout(retryTimeout);
      es?.close();
    };
  }, []);
}
