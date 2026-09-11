import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";
import { logger } from "@/utils/logger";
import { API } from "@/utils/config";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ phone: string }> },
): Promise<NextResponse> {
  const token = (await cookies()).get("access_token")?.value;
  if (!token) return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });

  const { phone } = await params;
  try {
    const res = await fetch(`${API}/api/lookup/${encodeURIComponent(phone)}/`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    logger.error("proxy:lookup", "Backend unreachable", { phone, error: err });
    return NextResponse.json({ detail: "Failed to reach backend." }, { status: 502 });
  }
}
