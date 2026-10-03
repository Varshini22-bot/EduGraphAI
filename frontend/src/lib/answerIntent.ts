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
  settings: Pick<SettingsPreferences, "marksPreference" | "explanationMode">,
  subject?: string | null
): string {
  const subjectSuffix = subject && subject !== "all" ? ` [Subject: ${subject.toUpperCase()}]` : "";

  // If the user already specified marks themselves ("...for 10 marks"),
  // never override their explicit wording — respect what they typed.
  if (MARKS_MENTION_PATTERN.test(rawQuery)) {
    return `${rawQuery}${subjectSuffix}`;
  }

  const modePhrase = MODE_LABEL[settings.explanationMode];

  if (settings.marksPreference === "auto") {
    return `${rawQuery}${subjectSuffix} (please answer as ${modePhrase})`;
  }

  const marksPhrase = MARKS_LABEL[settings.marksPreference];
  return `${rawQuery}${subjectSuffix} (please answer for ${marksPhrase}, as ${modePhrase})`;
}

// ---------------------------------------------------------------------------
// CONTEXTUAL EDUCATIONAL ACTIONS (Explain simply, Short Answer, 5-Mark, etc.)
// ---------------------------------------------------------------------------

export type ContextualAction =
  | "explain_simpler"
  | "short_answer"
  | "five_mark_answer"
  | "ten_mark_answer"
  | "give_example"
  | "related_concepts"
  | "more_detail"
  | "revision_notes"
  | "viva_questions"
  | "exam_questions"
  | "prerequisites"
  | "compare";

const ACTION_INSTRUCTION: Record<ContextualAction, string> = {
  explain_simpler: "explain it more simply",
  short_answer: "give a concise short answer, for 2 marks",
  five_mark_answer: "give an exam-oriented answer, for 5 marks",
  ten_mark_answer: "give a comprehensive university exam answer, for 10 marks",
  give_example: "give a clear concrete example",
  related_concepts: "show related concepts and prerequisites",
  more_detail: "give a more detailed explanation",
  revision_notes: "create revision notes",
  viva_questions: "generate viva questions",
  exam_questions: "generate likely exam questions",
  prerequisites: "show the prerequisites",
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
  if (action === "short_answer" || action === "five_mark_answer" || action === "ten_mark_answer") {
    return `${topic} — ${instruction}`;
  }
  const marks = extractExplicitMarks(originalQuery);
  return marks
    ? `${topic} — ${instruction}, for ${marks}`
    : `${topic} — ${instruction}`;
}
