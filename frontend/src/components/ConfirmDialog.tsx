"use client";

interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmDialog({
  isOpen,
  title,
  description,
  confirmLabel = "Delete",
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-[150] flex items-center justify-center bg-black/50 p-4"
      onClick={onCancel}
    >
      <div
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="confirm-dialog-title"
        onClick={(e) => e.stopPropagation()}
        className="card w-full max-w-[380px] px-6 py-6 shadow-elevated animate-fadein"
      >
        <h2 id="confirm-dialog-title" className="mb-2 text-[16px] font-semibold text-ink-primary">
          {title}
        </h2>
        <p className="mb-6 text-[13.5px] leading-relaxed text-ink-secondary">
          {description}
        </p>
        <div className="flex justify-end gap-2">
          <button onClick={onCancel} className="btn-ghost !px-3.5 !py-2 text-[13px]">
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="rounded-lg border border-danger bg-danger-dim px-3.5 py-2 text-[13px] font-semibold text-danger transition-colors hover:bg-danger hover:text-white"
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
