interface TypingIndicatorProps {
  label?: string;
}

export default function TypingIndicator({
  label = "Thinking...",
}: TypingIndicatorProps) {
  return (
    <div className="flex items-center gap-2 self-start rounded-xl border border-border-subtle bg-surface px-3.5 py-2.5 text-[13px] text-ink-tertiary animate-fadein">
      <span className="h-1.5 w-1.5 rounded-full bg-teal animate-pulse2" />
      <span className="h-1.5 w-1.5 rounded-full bg-teal animate-pulse2 [animation-delay:150ms]" />
      <span className="h-1.5 w-1.5 rounded-full bg-teal animate-pulse2 [animation-delay:300ms]" />
      {label}
    </div>
  );
}
