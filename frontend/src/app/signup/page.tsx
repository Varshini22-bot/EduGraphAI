"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { signUp } from "@/lib/auth/authClient";
import { useAuth } from "@/context/AuthContext";

export default function SignupPage() {
  const router = useRouter();
  const { refreshUser } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!name.trim() || !email.trim() || !password.trim()) {
      setError("Please fill in all fields to continue.");
      return;
    }
    setIsSubmitting(true);
    setError(null);
    try {
      await signUp(name.trim(), email.trim(), password);
      await refreshUser();
      router.push("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign up failed. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="card w-full max-w-[400px] px-7 py-7">
        <h1 className="mb-1 font-display text-[19px] font-bold text-ink-primary">
          Create your account
        </h1>
        <p className="mb-5 text-[13px] text-ink-secondary">
          Sign up to save your chat history, bookmarks, and progress.
        </p>

        {error && <div className="mb-3 text-[12.5px] text-danger">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="mb-3.5">
            <label className="mb-1.5 block text-[12.5px] font-medium text-ink-secondary">
              Full name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ada Lovelace"
              className="w-full rounded-lg border border-border-subtle bg-inputbg px-3 py-2.5 text-sm text-ink-primary outline-none focus:border-teal focus:shadow-[0_0_0_3px_rgba(69,214,198,0.14)]"
            />
          </div>
          <div className="mb-3.5">
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
          <div className="mb-4">
            <label className="mb-1.5 block text-[12.5px] font-medium text-ink-secondary">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full rounded-lg border border-border-subtle bg-inputbg px-3 py-2.5 text-sm text-ink-primary outline-none focus:border-teal focus:shadow-[0_0_0_3px_rgba(69,214,198,0.14)]"
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="btn-primary w-full"
          >
            {isSubmitting ? "Please wait..." : "Create Account"}
          </button>
        </form>

        <div className="mt-4 text-center text-[12.5px] text-ink-tertiary">
          Already have an account?{" "}
          <Link href="/login" className="font-semibold text-teal">
            Log in
          </Link>
        </div>
      </div>
    </div>
  );
}
