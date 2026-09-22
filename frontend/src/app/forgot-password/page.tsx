"use client";

import Link from "next/link";

export default function ForgotPasswordPage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="card w-full max-w-[420px] px-7 py-7">
        <h1 className="mb-1 font-display text-[19px] font-bold text-ink-primary">
          Password Recovery
        </h1>
        <p className="mb-5 text-[13px] text-ink-secondary">
          Academic system administration guidance
        </p>

        <div className="rounded-lg border border-border-subtle bg-surface-muted/40 p-4 mb-5 text-[13px] text-ink-secondary leading-relaxed space-y-3">
          <div className="flex items-start gap-2.5">
            <span className="text-teal font-bold text-[14px]">ℹ</span>
            <p className="text-ink-primary font-medium">
              Automated email password reset is not configured.
            </p>
          </div>
          <p>
            In this deployment, automated self-service email dispatch is disabled. If you have forgotten your password or need your student/evaluator account credentials reset, please contact the course instructor or system administrator.
          </p>
          <div className="pt-2 text-[12px] text-ink-tertiary border-t border-border-subtle/50">
            Administrator contact: <span className="text-ink-primary font-mono">admin@edugraphai.edu</span>
          </div>
        </div>

        <div className="mt-4 text-center text-[12.5px] text-ink-tertiary">
          <Link href="/login" className="font-semibold text-teal">
            &larr; Back to log in
          </Link>
        </div>
      </div>
    </div>
  );
}
