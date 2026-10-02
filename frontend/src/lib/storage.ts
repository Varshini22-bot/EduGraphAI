import { Bookmark, Conversation } from "./types";

// ---------------------------------------------------------------------------
// localStorage persistence. Frontend-only — nothing here talks to the
// backend. Every function is defensive: localStorage can be unavailable
// (SSR, private browsing) or contain corrupted/foreign data, and none of
// that should crash the app.
//
// SCOPING: keys are namespaced by an optional `scope` (the signed-in
// user's id). This fixes a real data-leak: previously every user on the
// same browser shared one fixed key, so signing in as a different person
// (or just visiting signed out) showed whoever last used that browser's
// chats. Passing no scope (signed out) uses a separate "guest" namespace,
// so anonymous browsing never sees a signed-in user's data and vice versa.
// ---------------------------------------------------------------------------

const GUEST_SCOPE = "guest";

function normalizeScope(scope?: string | null): string {
  if (!scope || typeof scope !== "string") return GUEST_SCOPE;
  const trimmed = scope.trim();
  return trimmed.length > 0 ? trimmed : GUEST_SCOPE;
}

function conversationsKey(scope?: string | null): string {
  return `kg-learning-assistant:conversations:${normalizeScope(scope)}`;
}

function bookmarksKey(scope?: string | null): string {
  return `kg-learning-assistant:bookmarks:${normalizeScope(scope)}`;
}

function isConversation(value: unknown): value is Conversation {
  if (!value || typeof value !== "object") return false;
  const v = value as Record<string, unknown>;
  return (
    typeof v.id === "string" &&
    typeof v.title === "string" &&
    typeof v.createdAt === "string" &&
    typeof v.updatedAt === "string" &&
    Array.isArray(v.messages)
  );
}

function isBookmark(value: unknown): value is Bookmark {
  if (!value || typeof value !== "object") return false;
  const v = value as Record<string, unknown>;
  return (
    typeof v.id === "string" &&
    typeof v.topic === "string" &&
    typeof v.answerSnippet === "string" &&
    typeof v.savedAt === "string"
  );
}

function readArray<T>(key: string, guard: (v: unknown) => v is T): T[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(key);
    if (!raw) return [];
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter(guard);
  } catch {
    return [];
  }
}

function writeArray<T>(key: string, value: T[]): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Quota exceeded or storage disabled — fail silently, app keeps
    // working in memory for the current session either way.
  }
}

export function clearGuestStorage(): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.removeItem("kg-learning-assistant:conversations:guest");
    window.localStorage.removeItem("kg-learning-assistant:conversations");
    window.localStorage.removeItem("kg-learning-assistant:bookmarks:guest");
    window.localStorage.removeItem("kg-learning-assistant:bookmarks");
  } catch {
    // Ignore storage errors in private browsing/restricted modes
  }
}

/**
 * @param scope Pass the signed-in user's id, or `null`/omit when signed out.
 * When not signed in, conversations are never persisted across sessions.
 */
export function loadConversations(scope?: string | null): Conversation[] {
  if (!scope || typeof scope !== "string" || !scope.trim()) {
    clearGuestStorage();
    return [];
  }
  return readArray(conversationsKey(scope), isConversation);
}

export function saveConversations(
  conversations: Conversation[],
  scope?: string | null
): void {
  if (!scope || typeof scope !== "string" || !scope.trim()) {
    clearGuestStorage();
    return;
  }
  writeArray(conversationsKey(scope), conversations);
}

export function loadBookmarks(scope?: string | null): Bookmark[] {
  if (!scope || typeof scope !== "string" || !scope.trim()) {
    clearGuestStorage();
    return [];
  }
  return readArray(bookmarksKey(scope), isBookmark);
}

export function saveBookmarks(bookmarks: Bookmark[], scope?: string | null): void {
  if (!scope || typeof scope !== "string" || !scope.trim()) {
    return;
  }
  writeArray(bookmarksKey(scope), bookmarks);
}
