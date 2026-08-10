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
