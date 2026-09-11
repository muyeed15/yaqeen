import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";
import { logger } from "@/utils/logger";
import { API } from "@/utils/config";

const PAGE_SIZE = process.env.PAGE_SIZE;
if (!PAGE_SIZE) throw new Error("PAGE_SIZE must be set in frontend/.env");

export function proxyList(backendPath: string) {
  return async function GET(request: NextRequest): Promise<NextResponse> {
    const token = (await cookies()).get("access_token")?.value;
    if (!token) return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });

    const page = request.nextUrl.searchParams.get("page") ?? "1";
    const url = `${API}${backendPath}?page=${page}&page_size=${PAGE_SIZE}`;
    try {
      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` },
        cache: "no-store",
      });
      return NextResponse.json(await res.json(), { status: res.status });
    } catch (err) {
      logger.error("proxy:list", `Backend unreachable`, { path: backendPath, error: err });
      return NextResponse.json({ detail: "Failed to reach backend." }, { status: 502 });
    }
  };
}
