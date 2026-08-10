"use client";

interface UpgradeDialogProps {
  isOpen: boolean;
  onUpgrade: () => void;
  onDismiss: () => void;
}

export default function UpgradeDialog({ isOpen, onUpgrade, onDismiss }: UpgradeDialogProps) {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-[160] flex items-center justify-center bg-black/50 p-4"
      onClick={onDismiss}
    >
      <div
        role="alertdialog"
        aria-modal="true"
        onClick={(e) => e.stopPropagation()}
        className="card w-full max-w-[380px] px-6 py-6 text-center shadow-elevated animate-fadein"
      >
        <div className="mb-3 text-3xl">⚡</div>
        <h2 className="mb-2 text-[16px] font-semibold text-ink-primary">
          You&apos;ve reached your free monthly limit.
        </h2>
        <p className="mb-6 text-[13.5px] leading-relaxed text-ink-secondary">
          Upgrade to Pro for ₹99/month for unlimited access.
        </p>
        <div className="flex flex-col gap-2">
          <button onClick={onUpgrade} className="btn-primary w-full">
            Upgrade to Pro
          </button>
          <button onClick={onDismiss} className="btn-ghost w-full">
            Maybe Later
          </button>
        </div>
      </div>
    </div>
  );
}
