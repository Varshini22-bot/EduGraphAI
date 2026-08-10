"use client";

import { useEffect, useState } from "react";
import { getUsage, UsageInfo } from "@/lib/api";

interface UsageIndicatorProps {
  onUpgradeClick: () => void;
  refreshKey?: number;
}

export default function UsageIndicator({ onUpgradeClick, refreshKey }: UsageIndicatorProps) {
  const [usage, setUsage] = useState<UsageInfo | null>(null);
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    let cancelled = false;
    getUsage().then((result) => {
      if (!cancelled) {
        setUsage(result);
        setChecked(true);
      }
    });
    return () => {
      cancelled = true;
    };
    // refreshKey lets the caller (page.tsx) force a re-check right after a
    // successful AI request, so the count updates without a full reload.
  }, [refreshKey]);

  // Nothing to show until we've checked, and nothing to show if the
  // backend doesn't support usage tracking yet (usage === null after
  // checking) — never invent a fake "unlimited" or fake limit.
  if (!checked || !usage) return null;

  const isPro = usage.plan === "pro" && usage.status === "active";

  if (isPro) {
    return (
      <div className="mb-2 rounded-lg border border-teal/30 bg-teal-dim px-3 py-2 text-[11.5px]">
        <div className="font-semibold text-teal">PRO — unlimited</div>
        {usage.expiresAt && (
          <div className="mt-0.5 text-ink-tertiary">
            Renews {new Date(usage.expiresAt).toLocaleDateString()}
          </div>
        )}
      </div>
    );
  }

  if (usage.limit === null) return null; // no real limit reported — show nothing

  const remaining = Math.max(0, usage.limit - usage.used);
  const isAtLimit = remaining === 0;
  const percentUsed = Math.min(100, Math.round((usage.used / usage.limit) * 100));

  return (
    <div className="mb-2 rounded-lg border border-border-subtle bg-elevated px-3 py-2.5">
      <div className="mb-1.5 flex items-center justify-between text-[11px]">
        <span className="font-semibold uppercase tracking-wide text-ink-tertiary">Free</span>
        <span className={isAtLimit ? "font-semibold text-danger" : "text-ink-tertiary"}>
          {remaining} remaining
        </span>
      </div>
      <div className="mb-1.5 text-[11.5px] font-medium text-ink-secondary">
        {usage.used} / {usage.limit} questions used
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-hoverbg">
        <div
          className={`h-full rounded-full ${isAtLimit ? "bg-danger" : "bg-teal"}`}
          style={{ width: `${percentUsed}%` }}
        />
      </div>
      {isAtLimit && (
        <button
          onClick={onUpgradeClick}
          className="mt-2 w-full rounded-md bg-teal py-1.5 text-[11.5px] font-semibold text-[#05221f]"
        >
          Upgrade to Pro
        </button>
      )}
    </div>
  );
}
