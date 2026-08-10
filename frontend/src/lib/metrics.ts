import { Bookmark, Conversation, DashboardMetrics, SubjectProgress } from "./types";

// ---------------------------------------------------------------------------
// Every number here is derived purely from data already in the frontend
// (conversations + bookmarks) — no backend endpoint for this exists yet, per
// "for now calculate from frontend data". Two heuristics worth noting:
//
// - "Learning Paths Completed" counts responses that included a non-empty
//   learning_path array (a proxy for "a path was shown"), since there's no
//   concept of a path being "finished" on the frontend or backend yet.
// - Each subject's progress bar assumes 10 distinct topics = 100% mastery.
//   That denominator is an arbitrary placeholder for a visual, not a real
//   curriculum size — swap it out once the backend can report subject scope.
// ---------------------------------------------------------------------------

const ASSUMED_TOPICS_PER_SUBJECT = 10;

export function computeDashboardMetrics(
  conversations: Conversation[],
  bookmarks: Bookmark[]
): DashboardMetrics {
  let totalQuestions = 0;
  let learningPathsCompleted = 0;
  const topicTimestamps: { topic: string; timestamp: string }[] = [];
  const subjectTopics = new Map<string, Set<string>>();
  const learnedTopics = new Set<string>();

  for (const conversation of conversations) {
    for (const message of conversation.messages) {
      totalQuestions += 1;
      if (!message.response) continue;

      const { topic, learning_path, graph_context } = message.response;
      learnedTopics.add(topic);
      topicTimestamps.push({ topic, timestamp: message.timestamp });

      if (learning_path.length > 0) {
        learningPathsCompleted += 1;
      }

      for (const item of graph_context) {
        if (item.relation !== "HAS_TOPIC") continue;
        const subject = item.related;
        if (!subjectTopics.has(subject)) {
          subjectTopics.set(subject, new Set());
        }
        subjectTopics.get(subject)!.add(topic);
      }
    }
  }

  const recentlyLearned = [...topicTimestamps]
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .map((t) => t.topic)
    .filter((topic, index, arr) => arr.indexOf(topic) === index)
    .slice(0, 6);

  const subjects: SubjectProgress[] = [...subjectTopics.entries()]
    .map(([subject, topics]) => ({
      subject,
      topicsExplored: topics.size,
      percent: Math.min(
        100,
        Math.round((topics.size / ASSUMED_TOPICS_PER_SUBJECT) * 100)
      ),
    }))
    .sort((a, b) => b.percent - a.percent);

  return {
    totalQuestions,
    topicsLearned: learnedTopics.size,
    bookmarkedTopics: bookmarks.length,
    learningPathsCompleted,
    recentlyLearned,
    subjects,
  };
}
