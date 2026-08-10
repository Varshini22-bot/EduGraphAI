import { Bookmark, Conversation } from "./types";

// ---------------------------------------------------------------------------
// localStorage persistence. Frontend-only — nothing here talks to the
// backend. Every function is defensive: localStorage can be unavailable
// (SSR, private browsing) or contain corrupted/foreign data, and none of
// that should crash the app.
// ---------------------------------------------------------------------------

const CONVERSATIONS_KEY = "kg-learning-assistant:conversations";
const BOOKMARKS_KEY = "kg-learning-assistant:bookmarks";

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

export function loadConversations(): Conversation[] {
  return readArray(CONVERSATIONS_KEY, isConversation);
}

export function saveConversations(conversations: Conversation[]): void {
  writeArray(CONVERSATIONS_KEY, conversations);
}

export function loadBookmarks(): Bookmark[] {
  return readArray(BOOKMARKS_KEY, isBookmark);
}

export function saveBookmarks(bookmarks: Bookmark[]): void {
  writeArray(BOOKMARKS_KEY, bookmarks);
}
