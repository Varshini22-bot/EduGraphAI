interface RecommendationsProps {
  topics: string[];
  onSelectTopic: (topic: string) => void;
}

export default function Recommendations({
  topics,
  onSelectTopic,
}: RecommendationsProps) {
  if (topics.length === 0) return null;

  return (
    <div className="animate-fadein" aria-label="Recommended topics">
      <div className="mb-2.5 text-[12px] font-semibold uppercase tracking-wide text-ink-tertiary">
        Continue learning
      </div>
      <div className="flex flex-wrap gap-2">
        {topics.map((topic) => (
          <button
            key={topic}
            onClick={() => onSelectTopic(topic)}
            className="inline-flex items-center gap-1.5 rounded-full border border-border-subtle bg-elevated py-1.5 px-3.5 text-[13px] font-medium text-ink-primary transition-colors hover:border-teal hover:bg-hoverbg"
          >
            {topic}
            <span className="text-teal" aria-hidden="true">↗</span>
          </button>
        ))}
      </div>
    </div>
  );
}
