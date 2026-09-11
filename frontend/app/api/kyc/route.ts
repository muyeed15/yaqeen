import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { API } from "@/utils/config";
export async function GET() {
  const token = (await cookies()).get("access_token")?.value;
  if (!token) return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  try {
    const res = await fetch(`${API}/api/kyc/`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
    if (res.status === 204) return NextResponse.json(null);
    return NextResponse.json(await res.json(), { status: res.status });
  } catch {
    return NextResponse.json({ detail: "Failed to reach backend." }, { status: 502 });
  }
}
