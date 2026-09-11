import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";
import { logger } from "@/utils/logger";
import { API } from "@/utils/config";

export async function GET(request: NextRequest): Promise<NextResponse> {
  const token = (await cookies()).get("access_token")?.value;
  if (!token) return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  const params = request.nextUrl.searchParams.toString();
  const url = `${API}/api/billers/${params ? "?" + params : ""}`;
  try {
    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
    return NextResponse.json(await res.json(), { status: res.status });
  } catch (err) {
    logger.error("proxy:billers", "Backend unreachable", { error: err });
    return NextResponse.json({ detail: "Failed to reach backend." }, { status: 502 });
  }
}
