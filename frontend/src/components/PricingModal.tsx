"use client";

import { useState } from "react";
import { startProCheckout } from "@/lib/api";

interface PricingModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentPlan?: "free" | "pro";
}

const FREE_FEATURES = [
  "Limited AI questions/month",
  "Basic knowledge graph",
  "Basic learning path",
  "Limited voice usage",
];

const PRO_FEATURES = [
  "Unlimited AI questions",
  "Full knowledge graph exploration",
  "Full learning recommendations",
  "Voice interaction",
  "Advanced educational features",
  "Diagram generation",
];

// Loads Razorpay's checkout script on demand — only when the user actually
// tries to upgrade, and only if the backend confirms it's configured.
// Never loaded speculatively, never assumed to succeed.
function loadRazorpayScript(): Promise<boolean> {
  return new Promise((resolve) => {
    if ((window as any).Razorpay) {
      resolve(true);
      return;
    }
    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.onload = () => resolve(true);
    script.onerror = () => resolve(false);
    document.body.appendChild(script);
  });
}

export default function PricingModal({ isOpen, onClose, currentPlan = "free" }: PricingModalProps) {
  const [status, setStatus] = useState<
    "idle" | "starting" | "not_configured" | "unavailable" | "error"
  >("idle");

  if (!isOpen) return null;

  async function handleUpgradeClick() {
    setStatus("starting");
    const result = await startProCheckout();

    if (result.status === "not_configured") {
      setStatus("not_configured");
      return;
    }
    if (result.status === "unavailable") {
      setStatus("unavailable");
      return;
    }

    // status === "order_created" — a real order exists server-side.
    const loaded = await loadRazorpayScript();
    if (!loaded) {
      setStatus("error");
      return;
    }

    const razorpay = new (window as any).Razorpay({
      key: result.keyId,
      order_id: result.orderId,
      amount: result.amount,
      currency: result.currency,
      name: "EduGraphAI Pro",
      description: "Monthly subscription — ₹99/month",
      // NOTE: this handler receiving a callback does NOT itself grant Pro
      // access — it only informs the user. The backend's
      // POST /subscription/verify (checking Razorpay's signature
      // server-side) is the only thing that can ever activate the
      // subscription; this frontend never sets a local "isPremium" flag.
      handler: () => {
        setStatus("idle");
        onClose();
        window.location.reload(); // re-check real usage/plan from the server
      },
      modal: {
        ondismiss: () => setStatus("idle"),
      },
    });
    razorpay.open();
    setStatus("idle");
  }

  return (
    <div
      className="fixed inset-0 z-[150] flex items-center justify-center bg-black/50 p-4"
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="card w-full max-w-[560px] px-6 py-6 shadow-elevated animate-fadein"
      >
        <div className="mb-5 flex items-start justify-between">
          <div>
            <h2 className="text-[18px] font-bold text-ink-primary">Upgrade to Pro</h2>
            <p className="mt-1 text-[13px] text-ink-secondary">
              Unlock unlimited learning with EduGraphAI Pro.
            </p>
          </div>
          <button
            onClick={onClose}
            aria-label="Close"
            className="text-ink-tertiary hover:text-ink-primary"
          >
            ✕
          </button>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="rounded-xl border border-border-subtle bg-elevated p-4">
            <div className="mb-1 text-[13px] font-semibold text-ink-primary">Free</div>
            <div className="mb-3 text-[22px] font-bold text-ink-primary">₹0</div>
            <ul className="flex flex-col gap-2">
              {FREE_FEATURES.map((f) => (
                <li key={f} className="flex gap-2 text-[12.5px] text-ink-secondary">
                  <span className="text-ink-tertiary">–</span>
                  {f}
                </li>
              ))}
            </ul>
            {currentPlan === "free" && (
              <div className="mt-4 rounded-md bg-hoverbg px-2.5 py-1 text-center text-[11.5px] font-semibold text-ink-secondary">
                Current plan
              </div>
            )}
          </div>

          <div className="rounded-xl border-2 border-teal bg-teal-dim p-4">
            <div className="mb-1 text-[13px] font-semibold text-teal">Pro</div>
            <div className="mb-3 text-[22px] font-bold text-ink-primary">
              ₹99<span className="text-[13px] font-medium text-ink-secondary">/month</span>
            </div>
            <ul className="flex flex-col gap-2">
              {PRO_FEATURES.map((f) => (
                <li key={f} className="flex gap-2 text-[12.5px] text-ink-primary">
                  <span className="text-teal">✓</span>
                  {f}
                </li>
              ))}
            </ul>
            {currentPlan === "pro" ? (
              <div className="mt-4 rounded-md bg-teal px-2.5 py-1 text-center text-[11.5px] font-semibold text-[#05221f]">
                Current plan
              </div>
            ) : (
              <button
                onClick={handleUpgradeClick}
                disabled={status === "starting"}
                className="mt-4 w-full rounded-md border border-teal/50 bg-elevated py-2 text-[12.5px] font-semibold text-teal transition-colors hover:bg-teal/10 disabled:cursor-not-allowed disabled:opacity-70"
              >
                {status === "starting" ? "Starting checkout..." : "Upgrade to Pro"}
              </button>
            )}
          </div>
        </div>

        {status === "not_configured" && (
          <p className="mt-4 rounded-lg border border-amber/30 bg-amber-dim px-3.5 py-2.5 text-center text-[12px] text-ink-primary">
            Payment integration isn&apos;t configured on the server yet — no
            charge can be made until it is.
          </p>
        )}
        {status === "unavailable" && (
          <p className="mt-4 rounded-lg border border-border-subtle bg-elevated px-3.5 py-2.5 text-center text-[12px] text-ink-secondary">
            Upgrade isn&apos;t available right now — please try again later.
          </p>
        )}
        {status === "error" && (
          <p className="mt-4 rounded-lg border border-danger/30 bg-danger-dim px-3.5 py-2.5 text-center text-[12px] text-ink-primary">
            Could not load the payment window. Please try again.
          </p>
        )}
        {status === "idle" && (
          <p className="mt-4 text-center text-[11.5px] text-ink-tertiary">
            Your subscription is only ever activated after a verified payment —
            never by this screen alone.
          </p>
        )}
      </div>
    </div>
  );
}
