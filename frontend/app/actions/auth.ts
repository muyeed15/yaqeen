"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { API } from "./_shared";

export type LoginState = { error: string | null };

export async function loginAction(_prev: LoginState, formData: FormData): Promise<LoginState> {
  const phone = formData.get("phone") as string;
  const password = formData.get("password") as string;

  if (!phone || !password) return { error: "Phone and password are required." };

  let data: { access: string; refresh: string };
  try {
    const res = await fetch(`${API}/api/token/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone, password }),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      return { error: body?.detail ?? body?.non_field_errors?.[0] ?? "Invalid phone or password." };
    }
    data = await res.json();
  } catch {
    return { error: "Could not reach the server. Is Django running?" };
  }

  const cookieStore = await cookies();
  const accessValue = process.env.ACCESS_TOKEN_MINUTES;
  const refreshValue = process.env.REFRESH_TOKEN_MINUTES;
  if (!accessValue || !refreshValue)
    throw new Error("Token lifetimes must be set in frontend/.env");
  const accessMinutes = parseInt(accessValue);
  const refreshMinutes = parseInt(refreshValue);

  cookieStore.set("access_token", data.access, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: accessMinutes * 60,
  });
  cookieStore.set("refresh_token", data.refresh, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: refreshMinutes * 60,
  });

  redirect("/dashboard");
}

export async function logoutAction(): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.delete("access_token");
  cookieStore.delete("refresh_token");
  redirect("/login");
}
