"use client";

import { useEffect, useRef, useState } from "react";
import { buildContextualActionQuery, ContextualAction } from "@/lib/answerIntent";

type SpeechState = "idle" | "speaking" | "paused";

interface ResponseActionsProps {
  answerText: string;
  topic: string;
  originalQuery: string;
  isBookmarked: boolean;
  onToggleBookmark: () => void;
  onRegenerate: () => void;
  onSelectTopic: (query: string) => void;
}

function isSpeechSynthesisSupported(): boolean {
  return typeof window !== "undefined" && "speechSynthesis" in window;
}

// ---------------------------------------------------------------------------
// Read Aloud reads the ANSWER DATA (the answerText prop), never the rendered
// DOM — so action-bar labels/icons (Copy, Bookmark, Regenerate, ⋯, ▶, ■ …)
// can never leak into speech. This strips the Markdown *scaffolding* the
// answer text carries (heading #, list bullets, emphasis/code marks, link
// URLs, and horizontal-rule / setext separator lines) so the synthesizer
// speaks the prose, not "hash", "asterisk", or "dash dash dash".
//
// Deliberately conservative: only whole-line separators (e.g. "---", "***",
// "-------------") are removed. Ordinary hyphens and em-dashes inside a
// sentence are meaningful in educational answers and are left untouched.
// ---------------------------------------------------------------------------
function cleanTextForSpeech(text: string): string {
  return text
    // Horizontal rules / setext underlines: a whole line of only -, *, _ or =
    // (3+), e.g. "---", "***", "_____", "=====", "-------------".
    .replace(/^[ \t]*([-*_=])(?:[ \t]*\1){2,}[ \t]*$/gm, "\n")
    // Leading heading markers: "### Title" -> "Title"
    .replace(/^[ \t]*#{1,6}[ \t]+/gm, "")
    // Leading list bullets: "- item" / "* item" / "+ item" / "• item" -> "item"
    .replace(/^[ \t]*[-*+•][ \t]+/gm, "")
    // Blockquote marker: "> quote" -> "quote"
    .replace(/^[ \t]*>[ \t]?/gm, "")
    // Markdown links: "[text](url)" -> "text"
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    // Inline emphasis / inline-code markers (**bold**, _italic_, `code`)
    .replace(/[`*_]/g, "")
    // Collapse the whitespace/newlines left behind into single spaces
    .replace(/\s+/g, " ")
    .trim();
}

// Educational follow-up actions — each maps to a stable ContextualAction
// key (not a free-form sentence template). The actual query text is built
// by buildContextualActionQuery(), which anchors the topic first and
// preserves the original marks — see answerIntent.ts for why.
const MORE_ACTIONS: { label: string; action: ContextualAction }[] = [
  { label: "Explain simpler", action: "explain_simpler" },
  { label: "More detail", action: "more_detail" },
  { label: "Revision notes", action: "revision_notes" },
  { label: "Viva questions", action: "viva_questions" },
  { label: "Exam questions", action: "exam_questions" },
  { label: "Short quiz", action: "short_quiz" },
  { label: "Prerequisites", action: "prerequisites" },
  { label: "Related concepts", action: "related_concepts" },
  { label: "Compare", action: "compare" },
];

export default function ResponseActions({
  answerText,
  topic,
  originalQuery,
  isBookmarked,
  onToggleBookmark,
  onRegenerate,
  onSelectTopic,
}: ResponseActionsProps) {
  const [copied, setCopied] = useState(false);
  const [speechState, setSpeechState] = useState<SpeechState>("idle");
  const [speechError, setSpeechError] = useState<string | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const menuButtonRef = useRef<HTMLButtonElement>(null);

  // Stop any speech if this message unmounts (e.g. conversation switched).
  useEffect(() => {
    return () => {
      if (isSpeechSynthesisSupported()) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  // Close the More menu on outside click and on Escape.
  useEffect(() => {
    if (!menuOpen) return;

    function handlePointerDown(event: MouseEvent | TouchEvent) {
      const target = event.target as Node;
      if (
        menuRef.current &&
        !menuRef.current.contains(target) &&
        menuButtonRef.current &&
        !menuButtonRef.current.contains(target)
      ) {
        setMenuOpen(false);
      }
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setMenuOpen(false);
        menuButtonRef.current?.focus();
      }
    }

    document.addEventListener("mousedown", handlePointerDown);
    document.addEventListener("touchstart", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
      document.removeEventListener("touchstart", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [menuOpen]);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(answerText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setSpeechError("Could not copy — clipboard access was denied.");
      setTimeout(() => setSpeechError(null), 3000);
    }
  }

  function handlePlay() {
    if (!isSpeechSynthesisSupported()) {
      setSpeechError("Text-to-speech isn't supported in this browser.");
      setTimeout(() => setSpeechError(null), 3000);
      return;
    }

    if (speechState === "paused") {
      window.speechSynthesis.resume();
      setSpeechState("speaking");
      return;
    }

    window.speechSynthesis.cancel();
    // Speak the cleaned ANSWER text only. Fall back to the raw answer on the
    // (practically impossible) chance cleaning empties it, so Read Aloud is
    // never silently a no-op.
    const speechText = cleanTextForSpeech(answerText) || answerText;
    const utterance = new SpeechSynthesisUtterance(speechText);
    utterance.onend = () => setSpeechState("idle");
    utterance.onerror = () => {
      setSpeechState("idle");
      setSpeechError("Playback failed.");
      setTimeout(() => setSpeechError(null), 3000);
    };
    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
    setSpeechState("speaking");
  }

  function handlePause() {
    if (!isSpeechSynthesisSupported()) return;
    window.speechSynthesis.pause();
    setSpeechState("paused");
  }

  function handleStop() {
    if (!isSpeechSynthesisSupported()) return;
    window.speechSynthesis.cancel();
    setSpeechState("idle");
  }

  function handleMoreAction(action: ContextualAction) {
    onSelectTopic(buildContextualActionQuery(topic, action, originalQuery));
    setMenuOpen(false);
  }

  return (
    <div className="relative flex flex-wrap items-center gap-0.5 pt-1">
      <button
        onClick={handleCopy}
        title="Copy answer"
        aria-label="Copy answer"
        className="flex items-center gap-1 rounded-md px-2 py-1 text-[11.5px] text-ink-tertiary transition-colors hover:bg-hoverbg hover:text-ink-primary"
      >
        {copied ? "✓" : "⧉"} <span className="hidden sm:inline">{copied ? "Copied" : "Copy"}</span>
      </button>

      {speechState === "idle" && (
        <button
          onClick={handlePlay}
          title="Read aloud"
          aria-label="Read answer aloud"
          className="flex items-center gap-1 rounded-md px-2 py-1 text-[11.5px] text-ink-tertiary transition-colors hover:bg-hoverbg hover:text-ink-primary"
        >
          ▶ <span className="hidden sm:inline">Read aloud</span>
        </button>
      )}
      {speechState === "speaking" && (
        <>
          <button
            onClick={handlePause}
            aria-label="Pause reading"
            className="flex items-center gap-1 rounded-md px-2 py-1 text-[11.5px] text-teal"
          >
            ❚❚ <span className="hidden sm:inline">Pause</span>
          </button>
          <button
            onClick={handleStop}
            aria-label="Stop reading"
            className="flex items-center gap-1 rounded-md px-2 py-1 text-[11.5px] text-ink-tertiary hover:text-ink-primary"
          >
            ■ <span className="hidden sm:inline">Stop</span>
          </button>
        </>
      )}
      {speechState === "paused" && (
        <>
          <button
            onClick={handlePlay}
            aria-label="Resume reading"
            className="flex items-center gap-1 rounded-md px-2 py-1 text-[11.5px] text-teal"
          >
            ▶ <span className="hidden sm:inline">Resume</span>
          </button>
          <button
            onClick={handleStop}
            aria-label="Stop reading"
            className="flex items-center gap-1 rounded-md px-2 py-1 text-[11.5px] text-ink-tertiary hover:text-ink-primary"
          >
            ■ <span className="hidden sm:inline">Stop</span>
          </button>
        </>
      )}

      <button
        onClick={onToggleBookmark}
        title={isBookmarked ? "Remove bookmark" : "Bookmark this answer"}
        aria-label={isBookmarked ? "Remove bookmark" : "Bookmark this answer"}
        aria-pressed={isBookmarked}
        className={`flex items-center gap-1 rounded-md px-2 py-1 text-[11.5px] transition-colors hover:bg-hoverbg ${
          isBookmarked ? "text-amber" : "text-ink-tertiary hover:text-ink-primary"
        }`}
      >
        {isBookmarked ? "★" : "☆"} <span className="hidden sm:inline">Bookmark</span>
      </button>

      <button
        onClick={onRegenerate}
        title="Regenerate answer"
        aria-label="Regenerate answer"
        className="flex items-center gap-1 rounded-md px-2 py-1 text-[11.5px] text-ink-tertiary transition-colors hover:bg-hoverbg hover:text-ink-primary"
      >
        ↻ <span className="hidden sm:inline">Regenerate</span>
      </button>

      <button
        ref={menuButtonRef}
        onClick={() => setMenuOpen((prev) => !prev)}
        title="More actions"
        aria-label="More actions"
        aria-haspopup="menu"
        aria-expanded={menuOpen}
        className={`flex items-center rounded-md px-2 py-1 text-[13px] transition-colors hover:bg-hoverbg ${
          menuOpen ? "bg-hoverbg text-ink-primary" : "text-ink-tertiary hover:text-ink-primary"
        }`}
      >
        ⋯
      </button>

      {menuOpen && (
        <div
          ref={menuRef}
          role="menu"
          aria-label="More response actions"
          className="absolute right-0 top-full z-20 mt-1 w-52 overflow-hidden rounded-lg border border-border-subtle bg-elevated py-1 shadow-elevated animate-fadein"
        >
          {MORE_ACTIONS.map((action) => (
            <button
              key={action.label}
              role="menuitem"
              onClick={() => handleMoreAction(action.action)}
              className="block w-full px-3 py-2 text-left text-[12.5px] text-ink-secondary transition-colors hover:bg-hoverbg hover:text-ink-primary"
            >
              {action.label}
            </button>
          ))}
        </div>
      )}

      {speechError && <span className="text-[11px] text-danger">{speechError}</span>}
    </div>
  );
}
