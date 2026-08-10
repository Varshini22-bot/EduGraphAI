"use client";

import Link from "next/link";
import { useAuth } from "@/context/AuthContext";

export default function ProfilePage() {
  const { user, loading } = useAuth();

  if (!loading && !user) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-3 px-4 text-center">
        <p className="text-[14px] text-ink-secondary">
          You need to be signed in to view your profile.
        </p>
        <Link href="/login" className="btn-primary">
          Sign In
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-[560px] px-6 py-10">
      <Link href="/" className="mb-6 inline-block text-[13px] text-ink-tertiary hover:text-ink-primary">
        ← Back to app
      </Link>
      <h1 className="mb-6 font-display text-2xl font-bold text-ink-primary">
        Profile
      </h1>

      {user && (
        <div className="card px-6 py-6">
          <div className="mb-5 flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-violet to-[#5c53c9] text-xl font-bold text-white">
              {(user.full_name || user.email).charAt(0).toUpperCase()}
            </div>
            <div>
              <div className="font-display text-lg font-bold text-ink-primary">
                {user.full_name || user.email}
              </div>
              <div className="text-[13px] text-ink-tertiary">{user.email}</div>
            </div>
          </div>

          <div className="flex items-center justify-between border-t border-border-subtle pt-4">
            <span className="text-[13px] text-ink-secondary">Account Status</span>
            <span
              className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                user.is_active ? "bg-teal-dim text-teal" : "bg-danger-dim text-danger"
              }`}
            >
              {user.is_active ? "Active" : "Inactive"}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
