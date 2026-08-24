import { ExplanationMode, MarksPreference, SettingsPreferences } from "./settingsStorage";

// ---------------------------------------------------------------------------
// The verified /ask contract is GET /ask?query=<text> — a single string,
// nothing else. There is no marks/explanation-mode parameter to send
// separately (confirmed against api/routes.py earlier in this project).
//
// Rather than pretend these settings have no effect (cosmetic-only), this
// appends the user's actual intent into the query text itself before
// sending — the LLM genuinely sees "...for 7-8 marks" etc. This is honest:
// it changes what's actually sent to the backend, not just how the
// response is displayed afterward.
//
// It never touches what's displayed as the user's message (ChatMessage.query
// stays exactly what they typed) — only what's sent to askQuestion().
// ---------------------------------------------------------------------------

const MARKS_LABEL: Record<Exclude<MarksPreference, "auto">, string> = {
  "2": "2 marks",
  "5": "5 marks",
  "7-8": "7-8 marks",
  "10": "10 marks",
  "15": "15 marks",
};

const MODE_LABEL: Record<ExplanationMode, string> = {
  definition: "a concise definition",
  "step-by-step": "a step-by-step explanation",
  "exam-answer": "an exam-friendly answer",
  "revision-notes": "revision notes",
};

const MARKS_MENTION_PATTERN = /\bmarks?\b/i;

export function buildAugmentedQuery(
  rawQuery: string,
  settings: Pick<SettingsPreferences, "marksPreference" | "explanationMode">
): string {
  // If the user already specified marks themselves ("...for 10 marks"),
  // never override their explicit wording — respect what they typed.
  if (MARKS_MENTION_PATTERN.test(rawQuery)) {
    return rawQuery;
  }

  const modePhrase = MODE_LABEL[settings.explanationMode];

  if (settings.marksPreference === "auto") {
    return `${rawQuery} (please answer as ${modePhrase})`;
  }

  const marksPhrase = MARKS_LABEL[settings.marksPreference];
  return `${rawQuery} (please answer for ${marksPhrase}, as ${modePhrase})`;
}

// ---------------------------------------------------------------------------
// CONTEXTUAL EDUCATIONAL ACTIONS (More detail, Explain simpler, etc.)
//
// BUG THIS FIXES: these actions were previously phrased as a normal new
// sentence (e.g. "Give a more detailed explanation of Binary Search") and
// sent through the exact same free-text pipeline as a fresh question. The
// backend's TopicExtractor only strips a fixed filler-word list (explain/
// describe/define/what is/etc.) — none of these action phrasings are in
// that list, so the full sentence survives, fails the whole-phrase graph
// match, and falls back to matching individual words. Whichever word hits
// any node first wins — which is how "detailed" could resolve to an
// unrelated node instead of "Binary Search".
//
// FIX (frontend-only, no backend access to change TopicExtractor itself):
// anchor the topic as the FIRST word(s) of the query, so the backend's own
// existing word-by-word fallback tries the real topic before any generic
// instruction word (detailed/simple/quiz/etc.) ever gets a chance to
// false-match an unrelated node. This reuses the existing extraction path
// exactly as-is — no duplicate topic-extraction logic is introduced here.
//
// This also fixes marks preservation: the ORIGINAL question's marks (e.g.
// "for 8 marks") are extracted from message.query and re-embedded verbatim,
// so buildAugmentedQuery's existing MARKS_MENTION_PATTERN check (above)
// sees them and leaves them untouched — it does NOT fall through to the
// user's global Settings marks preference, which was the second bug.
//
// NOTE — the fully robust fix would be a backend change: a new endpoint
// accepting {topic, action, marks} directly, skipping TopicExtractor
// entirely since the topic is already known. That's not implemented here
// (no backend write access); this is the best mitigation achievable
// entirely from the frontend.
// ---------------------------------------------------------------------------

export type ContextualAction =
  | "explain_simpler"
  | "more_detail"
  | "revision_notes"
  | "viva_questions"
  | "exam_questions"
  | "short_quiz"
  | "prerequisites"
  | "related_concepts"
  | "compare";

const ACTION_INSTRUCTION: Record<ContextualAction, string> = {
  explain_simpler: "explain it more simply",
  more_detail: "give a more detailed explanation",
  revision_notes: "create revision notes",
  viva_questions: "generate viva questions",
  exam_questions: "generate likely exam questions",
  short_quiz: "create a short quiz",
  prerequisites: "show the prerequisites",
  related_concepts: "show related concepts",
  compare: "compare it with a similar concept",
};

const MARKS_EXTRACT_PATTERN = /(\d{1,2}(?:\s*[-–]\s*\d{1,2})?)\s*marks?\b/i;

/**
 * Extracts an explicit marks mention from the ORIGINAL question that
 * produced the current topic (e.g. "Explain Binary Search for 8 marks"
 * → "8 marks"). Returns null if none was mentioned — callers should not
 * fabricate one, just proceed without it.
 */
export function extractExplicitMarks(originalQuery: string): string | null {
  const match = originalQuery.match(MARKS_EXTRACT_PATTERN);
  return match ? `${match[1]} marks` : null;
}

/**
 * Builds a query for a contextual educational action (More detail, Explain
 * simpler, etc.) that keeps the topic unchanged and carries forward the
 * original marks — topic-first phrasing so the backend's existing fallback
 * extraction resolves to the same topic instead of drifting to an
 * unrelated node.
 */
export function buildContextualActionQuery(
  topic: string,
  action: ContextualAction,
  originalQuery: string
): string {
  const instruction = ACTION_INSTRUCTION[action];
  const marks = extractExplicitMarks(originalQuery);
  return marks
    ? `${topic} — ${instruction}, for ${marks}`
    : `${topic} — ${instruction}`;
}
