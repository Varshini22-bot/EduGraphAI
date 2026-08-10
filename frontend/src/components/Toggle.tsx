interface ToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: string;
  description?: string;
  disabled?: boolean;
}

export default function Toggle({
  checked,
  onChange,
  label,
  description,
  disabled = false,
}: ToggleProps) {
  return (
    <div className="flex items-center justify-between gap-4 py-3">
      <div className="min-w-0">
        <div className="text-[13.5px] font-medium text-ink-primary">{label}</div>
        {description && (
          <div className="mt-0.5 text-[12px] text-ink-tertiary">{description}</div>
        )}
      </div>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        aria-label={label}
        disabled={disabled}
        onClick={() => onChange(!checked)}
        className={`relative h-6 w-11 flex-shrink-0 rounded-full border transition-colors ${
          checked
            ? "border-teal bg-teal-dim"
            : "border-border-subtle bg-elevated"
        } ${disabled ? "cursor-not-allowed opacity-50" : ""}`}
      >
        <span
          className={`absolute top-1/2 h-4 w-4 -translate-y-1/2 rounded-full transition-transform ${
            checked ? "translate-x-[22px] bg-teal" : "translate-x-1 bg-ink-tertiary"
          }`}
        />
      </button>
    </div>
  );
}
