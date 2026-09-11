import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { API } from "@/utils/config";

export async function GET(): Promise<NextResponse> {
  const token = (await cookies()).get("access_token")?.value;
  if (!token) return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });

  const res = await fetch(`${API}/api/me/`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  return NextResponse.json(await res.json(), { status: res.status });
}
