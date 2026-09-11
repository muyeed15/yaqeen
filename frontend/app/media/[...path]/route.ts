import { NextRequest, NextResponse } from "next/server";
import { logger } from "@/utils/logger";
import { API } from "@/utils/config";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> },
): Promise<NextResponse> {
  const { path } = await params;
  const url = `${API}/media/${path.join("/")}`;
  try {
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) {
      return new NextResponse(null, {
        status: res.status,
        headers: { "Cache-Control": "no-store" },
      });
    }
    const body = Buffer.from(await res.arrayBuffer());
    return new NextResponse(body, {
      headers: {
        "Content-Type": res.headers.get("Content-Type") ?? "application/octet-stream",
        "Cache-Control": "public, max-age=86400",
      },
    });
  } catch (err) {
    logger.error("proxy:media", "Backend unreachable", { path, error: err });
    return new NextResponse(null, { status: 502 });
  }
}
