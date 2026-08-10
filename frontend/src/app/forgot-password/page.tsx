"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { requestPasswordReset } from "@/lib/auth/authClient";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [sent, setSent] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!email.trim()) return;
    setIsSubmitting(true);
    await requestPasswordReset(email.trim());
    setIsSubmitting(false);
    setSent(true);
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="card w-full max-w-[400px] px-7 py-7">
        <h1 className="mb-1 font-display text-[19px] font-bold text-ink-primary">
          Reset your password
        </h1>
        <p className="mb-5 text-[13px] text-ink-secondary">
          Enter your email and we'll send you a link to reset your password.
        </p>

        {sent ? (
          <div className="rounded-lg border border-teal/30 bg-teal-dim px-3.5 py-3 text-[13px] text-ink-primary">
            If an account exists for {email}, a reset link is on its way.
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="mb-1.5 block text-[12.5px] font-medium text-ink-secondary">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full rounded-lg border border-border-subtle bg-inputbg px-3 py-2.5 text-sm text-ink-primary outline-none focus:border-teal focus:shadow-[0_0_0_3px_rgba(69,214,198,0.14)]"
              />
            </div>
            <button type="submit" disabled={isSubmitting} className="btn-primary w-full">
              {isSubmitting ? "Sending..." : "Send Reset Link"}
            </button>
          </form>
        )}

        <div className="mt-4 text-center text-[12.5px] text-ink-tertiary">
          <Link href="/login" className="font-semibold text-teal">
            Back to log in
          </Link>
        </div>
      </div>
    </div>
  );
}
