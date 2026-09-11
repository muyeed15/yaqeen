"use client";

import { useActionState } from "react";
import { loginAction } from "@/app/actions";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import Image from "next/image";
const initialState = { error: null };

export function LoginForm(): React.ReactElement {
  const [state, action, pending] = useActionState(loginAction, initialState);

  return (
    <div className="w-full max-w-sm relative z-10">
      <div className="text-center mb-8">
        <div className="flex items-center justify-center gap-2">
          <Image src="/logo.svg" alt="" width={40} height={40} />
          <h1 className="text-white text-2xl font-bold">Yaqeen</h1>
        </div>
      </div>

      <div className="bg-white border border-sage-mid rounded-xl p-6">
        <h2 className="text-navy font-semibold text-base mb-5">Sign in to your account</h2>

        {state.error && (
          <div className="mb-4 border-l-4 border-red-500 bg-red-50 px-4 py-3 text-sm text-red-700 rounded">
            {state.error}
          </div>
        )}

        <form action={action} className="space-y-4">
          <Input
            label="Phone Number"
            name="phone"
            type="tel"
            autoComplete="tel"
            required
            placeholder="01XXXXXXXXX"
          />
          <Input
            label="Password"
            name="password"
            type="password"
            autoComplete="current-password"
            required
            placeholder="••••••••"
          />
          <div className="pt-2">
            <Button type="submit" variant="primary" size="lg" loading={pending} className="w-full">
              {pending ? "Signing in…" : "Sign In"}
            </Button>
          </div>
        </form>
      </div>

      <p className="text-center text-xs text-white/40 mt-6">Yaqeen · Secure Digital Wallet</p>
    </div>
  );
}
