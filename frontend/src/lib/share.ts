import { Conversation } from "./types";

export interface ConversationPreviewData {
  hasContent: boolean;
  title: string;
  topic?: string | null;
  firstQuestion?: string;
  firstAnswerPreview?: string;
  messageCount: number;
}

export interface PreparedShareData {
  title: string;
  text: string;
  url: string;
  preview: ConversationPreviewData;
}

/**
 * Strips markdown symbols (headers, bold/italic, links, hr rules) so text
 * renders cleanly inside compact dialog previews without raw markup.
 */
function cleanPreviewText(text: string): string {
  return text
    .replace(/^[ \t]*([-*_=])(?:[ \t]*\1){2,}[ \t]*$/gm, " ")
    .replace(/^[ \t]*#{1,6}[ \t]+/gm, "")
    .replace(/^[ \t]*[-*+•][ \t]+/gm, "")
    .replace(/^[ \t]*>[ \t]?/gm, "")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/[`*_~]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

/**
 * Truncates text safely at word boundary with an ellipsis.
 */
function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  const sub = text.slice(0, maxLength);
  const lastSpace = sub.lastIndexOf(" ");
  return (lastSpace > 0 ? sub.slice(0, lastSpace) : sub).trim() + "…";
}

/**
 * Prepares the current conversation for frontend sharing.
 *
 * Stage 1 architecture:
 * - Creates a safe share target using the current application origin URL.
 * - Extracts a safe, privacy-preserving preview of the current active conversation.
 * - Never includes or exposes authentication tokens, API keys, session IDs,
 *   or private database IDs.
 */
export function prepareShareData(conversation: Conversation | null): PreparedShareData {
  const safeUrl =
    typeof window !== "undefined"
      ? window.location.origin
      : "https://edu-graph-ai.vercel.app";

  if (!conversation || !conversation.messages || conversation.messages.length === 0) {
    return {
      title: "EduGraphAI — Knowledge Graph Learning Assistant",
      text: "Explore academic concepts with EduGraphAI, an AI-powered Knowledge Graph learning assistant.",
      url: safeUrl,
      preview: {
        hasContent: false,
        title: conversation?.title || "New Chat",
        messageCount: 0,
      },
    };
  }

  // Find the first meaningful user query in the conversation
  const firstMsg =
    conversation.messages.find((m) => m.query && m.query.trim().length > 0) ||
    conversation.messages[0];

  const firstQuestion = firstMsg?.query?.trim() || "";
  const rawAnswer = firstMsg?.response?.answer || "";
  const cleanAnswer = cleanPreviewText(rawAnswer);
  const firstAnswerPreview = cleanAnswer ? truncateText(cleanAnswer, 180) : undefined;
  const topic = firstMsg?.response?.topic || null;

  const displayTitle =
    conversation.title && conversation.title !== "New Chat"
      ? `${conversation.title} | EduGraphAI`
      : topic
      ? `${topic} | EduGraphAI`
      : "EduGraphAI — Knowledge Graph Learning Assistant";

  const shareText = firstQuestion
    ? `Learning discussion on "${truncateText(firstQuestion, 60)}" via EduGraphAI`
    : "Explore academic topics with EduGraphAI Knowledge Graph Learning Assistant";

  return {
    title: displayTitle,
    text: shareText,
    url: safeUrl,
    preview: {
      hasContent: true,
      title: conversation.title || "Conversation",
      topic,
      firstQuestion: truncateText(firstQuestion, 120),
      firstAnswerPreview,
      messageCount: conversation.messages.length,
    },
  };
}

/**
 * Copies the share URL to the system clipboard.
 */
export async function copyShareLink(url: string): Promise<boolean> {
  if (
    typeof navigator !== "undefined" &&
    navigator.clipboard &&
    typeof navigator.clipboard.writeText === "function"
  ) {
    try {
      await navigator.clipboard.writeText(url);
      return true;
    } catch {
      return false;
    }
  }
  return false;
}

/**
 * Checks if native Web Share is supported in the current environment.
 */
export function isNativeShareSupported(): boolean {
  return typeof navigator !== "undefined" && typeof navigator.share === "function";
}

/**
 * Triggers native Web Share if supported. Handles user cancellation (AbortError) silently.
 */
export async function triggerNativeShare(data: {
  title: string;
  text?: string;
  url: string;
}): Promise<"shared" | "aborted" | "unsupported" | "error"> {
  if (!isNativeShareSupported()) return "unsupported";
  try {
    if (typeof navigator.canShare === "function" && !navigator.canShare(data)) {
      return "unsupported";
    }
    await navigator.share(data);
    return "shared";
  } catch (err) {
    if (err instanceof Error && err.name === "AbortError") {
      return "aborted";
    }
    return "error";
  }
}
