import { cookies } from "next/headers";
import { NextRequest } from "next/server";
import * as http from "http";
import * as https from "https";
import { logger } from "@/utils/logger";
import { API } from "@/utils/config";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET(request: NextRequest): Promise<Response> {
  const token = (await cookies()).get("access_token")?.value;
  if (!token) return new Response("Unauthorized", { status: 401 });

  const lastId = request.nextUrl.searchParams.get("last_id") ?? "0";
  const upstreamUrl = new URL(`/api/notifications/stream/?last_id=${lastId}`, API);

  const { readable, writable } = new TransformStream<Uint8Array, Uint8Array>();
  const writer = writable.getWriter();

  const lib = upstreamUrl.protocol === "https:" ? https : http;

  const upstreamReq = lib.get(
    upstreamUrl.toString(),
    { headers: { Authorization: `Bearer ${token}` } },
    (res) => {
      res.on("data", (chunk: Buffer) => void writer.write(chunk));
      res.on("end", () => void writer.close());
      res.on("error", (err) => {
        logger.error("proxy:sse", "Stream error from upstream", err);
        void writer.abort(err);
      });
    },
  );

  upstreamReq.on("error", (err) => {
    logger.error("proxy:sse", "Failed to connect to upstream SSE", err);
    void writer.abort(err);
  });

  request.signal.addEventListener("abort", () => {
    upstreamReq.destroy();
    void writer.abort();
  });

  return new Response(readable, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
      "X-Accel-Buffering": "no",
    },
  });
}
