interface LearningPathProps {
  steps: string[];
}

export default function LearningPath({ steps }: LearningPathProps) {
  if (steps.length === 0) return null;

  return (
    <div className="animate-fadein" aria-label="Learning path">
      <div className="mb-3 text-[12px] font-semibold uppercase tracking-wide text-ink-tertiary">
        Suggested learning path
      </div>
      <div className="flex flex-col">
        {steps.map((step, index) => (
          <div className="flex gap-3" key={`${step}-${index}`}>
            <div className="flex flex-col items-center flex-shrink-0">
              <div className="z-10 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full border border-teal font-mono text-[10.5px] font-semibold text-teal">
                {index + 1}
              </div>
              {index < steps.length - 1 && (
                <div className="my-0.5 w-px flex-1 bg-border-strong" />
              )}
            </div>
            <div className={`pt-px ${index === steps.length - 1 ? "" : "pb-3.5"}`}>
              <div className="text-[13.5px] font-medium text-ink-primary">{step}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
