import { GraphContextItem } from "@/lib/types";

interface RelatedTopicsProps {
  items: GraphContextItem[];
  onSelectTopic: (topic: string) => void;
}

export default function RelatedTopics({
  items,
  onSelectTopic,
}: RelatedTopicsProps) {
  if (items.length === 0) return null;

  return (
    <div className="animate-fadein" aria-label="Related topics">
      <div className="mb-2.5 text-[12px] font-semibold uppercase tracking-wide text-ink-tertiary">
        Key concepts
      </div>
      <div className="flex flex-wrap gap-2">
        {items.map((item, index) => (
          <button
            key={`${item.relation}-${item.related}-${index}`}
            onClick={() => onSelectTopic(item.related)}
            className="inline-flex items-center gap-1.5 rounded-full border border-border-subtle bg-elevated py-1.5 pl-1.5 pr-3 text-[13px] text-ink-primary transition-colors hover:border-teal hover:bg-hoverbg"
          >
            <span className="rounded-full bg-violet-dim px-1.5 py-0.5 font-mono text-[10px] font-medium text-violet">
              {item.relation}
            </span>
            {item.related}
          </button>
        ))}
      </div>
    </div>
  );
}
