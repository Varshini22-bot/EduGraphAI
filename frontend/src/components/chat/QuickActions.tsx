interface QuickActionsProps {
  topic: string;
  onAction: (query: string) => void;
}

// Each action builds a natural-language follow-up question and submits it
// through the exact same pipeline as clicking a Related Topic/Recommendation
// chip (onSelectTopic → onSubmitQuery) — it becomes the next message in the
// same conversation, so it reuses the existing context rather than
// introducing a separate state system or a new backend call.
const ACTIONS: { label: string; buildQuery: (topic: string) => string }[] = [
  { label: "Explain simpler", buildQuery: (t) => `Explain ${t} more simply` },
  { label: "More detail", buildQuery: (t) => `Give a more detailed explanation of ${t}` },
  { label: "Revision notes", buildQuery: (t) => `Create revision notes for ${t}` },
  { label: "Viva questions", buildQuery: (t) => `Generate viva questions for ${t}` },
  { label: "Exam questions", buildQuery: (t) => `Generate likely exam questions for ${t}` },
  { label: "Short quiz", buildQuery: (t) => `Create a short quiz on ${t}` },
  { label: "Prerequisites", buildQuery: (t) => `Show prerequisites for ${t}` },
  { label: "Related concepts", buildQuery: (t) => `Show related concepts for ${t}` },
  { label: "Compare", buildQuery: (t) => `Compare ${t} with a similar concept` },
];

export default function QuickActions({ topic, onAction }: QuickActionsProps) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {ACTIONS.map((action) => (
        <button
          key={action.label}
          onClick={() => onAction(action.buildQuery(topic))}
          className="rounded-full border border-border-subtle bg-elevated px-2.5 py-1 text-[11.5px] text-ink-secondary transition-colors hover:border-teal hover:text-ink-primary"
        >
          {action.label}
        </button>
      ))}
    </div>
  );
}
