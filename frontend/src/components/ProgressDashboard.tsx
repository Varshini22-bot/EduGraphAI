import { DashboardMetrics } from "@/lib/types";

interface ProgressDashboardProps {
  metrics: DashboardMetrics;
}

function StatCard({ value, label }: { value: number; label: string }) {
  return (
    <div className="card px-4.5 py-4.5">
      <div className="font-mono text-[26px] font-semibold text-teal">{value}</div>
      <div className="mt-1 text-xs text-ink-secondary">{label}</div>
    </div>
  );
}

export default function ProgressDashboard({ metrics }: ProgressDashboardProps) {
  return (
    <div className="mx-auto max-w-[920px] px-6 pb-16 pt-7">
      <h2 className="mb-1 font-display text-[22px] font-bold text-ink-primary">
        Progress Dashboard
      </h2>
      <p className="mb-6 text-[13.5px] text-ink-secondary">
        A snapshot of how much of the knowledge graph you've explored so far.
      </p>

      <div className="mb-7 grid grid-cols-2 gap-3.5 lg:grid-cols-4">
        <StatCard value={metrics.totalQuestions} label="Total Questions" />
        <StatCard value={metrics.topicsLearned} label="Topics Learned" />
        <StatCard value={metrics.bookmarkedTopics} label="Bookmarked Topics" />
        <StatCard
          value={metrics.learningPathsCompleted}
          label="Learning Paths Completed"
        />
      </div>

      <div className="mb-3 text-[13px] font-semibold uppercase tracking-wide text-ink-tertiary">
        Learning Progress
      </div>
      <div className="card mb-7 px-5 py-5">
        {metrics.subjects.length === 0 ? (
          <p className="text-[13.5px] text-ink-secondary">
            No subject data yet — subjects are detected automatically from
            each answer's related topics as you explore.
          </p>
        ) : (
          <div className="flex flex-col gap-4">
            {metrics.subjects.map((subject) => (
              <div key={subject.subject}>
                <div className="mb-1.5 flex items-center justify-between text-[13px]">
                  <span className="font-semibold text-ink-primary">
                    {subject.subject}
                  </span>
                  <span className="font-mono text-ink-secondary">
                    {subject.percent}%
                  </span>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-elevated">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-teal to-violet transition-all"
                    style={{ width: `${subject.percent}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="mb-3 text-[13px] font-semibold uppercase tracking-wide text-ink-tertiary">
        Recently Learned
      </div>
      <div className="card px-5 py-5">
        {metrics.recentlyLearned.length === 0 ? (
          <p className="text-[13.5px] text-ink-secondary">
            No topics explored yet — ask your first question to get started.
          </p>
        ) : (
          <div className="grid grid-cols-[repeat(auto-fill,minmax(160px,1fr))] gap-2.5">
            {metrics.recentlyLearned.map((topic) => (
              <div
                key={topic}
                className="flex items-center gap-2 rounded-lg border border-border-subtle bg-elevated px-3 py-2.5 text-[13px] text-ink-primary"
              >
                <span className="text-teal" aria-hidden="true">✓</span>
                {topic}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
