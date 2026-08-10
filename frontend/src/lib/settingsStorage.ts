// ---------------------------------------------------------------------------
// Local-only preference storage for the Settings page. Same defensive
// pattern as storage.ts: localStorage can be unavailable (SSR, private
// browsing) or contain corrupted/foreign data, and none of that should
// crash the app.
//
// IMPORTANT: these preferences are NOT currently read by any chat/graph
// rendering component (ChatMessage, RelatedTopics, LearningPath,
// Recommendations, GraphViewer, ChatInput). They are stored cleanly here
// for future integration, per the explicit instruction not to pretend
// unwired settings are already functional. See the "UI-only" list in the
// implementation summary for exactly which ones this applies to.
// ---------------------------------------------------------------------------

const SETTINGS_KEY = "kg-learning-assistant:settings";

export type ThemePreference = "system" | "light" | "dark";
export type AnswerStyle = "simple" | "detailed" | "exam-friendly";
export type LearningLevel = "beginner" | "intermediate" | "advanced";
export type MarksPreference = "auto" | "2" | "5" | "7-8" | "10" | "15";
export type ExplanationMode =
  | "definition"
  | "step-by-step"
  | "exam-answer"
  | "revision-notes";

export interface SettingsPreferences {
  // Appearance
  theme: ThemePreference;
  compactMode: boolean;

  // Learning preferences
  answerStyle: AnswerStyle;
  learningLevel: LearningLevel;
  marksPreference: MarksPreference;
  explanationMode: ExplanationMode;
  showGraphContext: boolean;
  showLearningPath: boolean;
  showRecommendations: boolean;

  // Chat preferences
  enterToSend: boolean;
  autoSaveConversations: boolean;

  // Knowledge graph preferences
  showRelatedTopics: boolean;
  showIncomingRelationships: boolean;
  showOutgoingRelationships: boolean;
}

export const DEFAULT_SETTINGS: SettingsPreferences = {
  theme: "dark",
  compactMode: false,
  answerStyle: "detailed",
  learningLevel: "intermediate",
  // Default mirrors your spec: "approximately a 7-8 mark exam-friendly
  // answer unless the user specifies another mark requirement."
  marksPreference: "7-8",
  explanationMode: "exam-answer",
  showGraphContext: true,
  showLearningPath: true,
  showRecommendations: true,
  enterToSend: true,
  autoSaveConversations: true,
  showRelatedTopics: true,
  showIncomingRelationships: true,
  showOutgoingRelationships: true,
};

function isValidSettings(value: unknown): value is Partial<SettingsPreferences> {
  return !!value && typeof value === "object";
}

export function loadSettings(): SettingsPreferences {
  if (typeof window === "undefined") return DEFAULT_SETTINGS;

  try {
    const raw = window.localStorage.getItem(SETTINGS_KEY);
    if (!raw) return DEFAULT_SETTINGS;

    const parsed: unknown = JSON.parse(raw);
    if (!isValidSettings(parsed)) return DEFAULT_SETTINGS;

    // Merge over defaults so a future new preference added here doesn't
    // come back as `undefined` for users with an older saved settings blob.
    return { ...DEFAULT_SETTINGS, ...parsed };
  } catch {
    return DEFAULT_SETTINGS;
  }
}

export function saveSettings(settings: SettingsPreferences): void {
  if (typeof window === "undefined") return;

  try {
    window.localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
  } catch {
    // Quota exceeded or storage disabled — fail silently, same as storage.ts.
  }
}
