"use client";

import { useEffect, useRef, useState } from "react";

interface ResponseActionsProps {
  answerText: string;
  topic: string;
  isBookmarked: boolean;
  onToggleBookmark: () => void;
  onRegenerate: () => void;
  onSelectTopic: (query: string) => void;
}

type SpeechState = "idle" | "speaking" | "paused";

function isSpeechSynthesisSupported(): boolean {
  return typeof window !== "undefined" && "speechSynthesis" in window;
}

// Educational follow-up actions — moved out of the always-visible row and
// into the "More" menu per this pass. Each still builds a natural-language
// follow-up and submits it through the same onSelectTopic → onSubmitQuery
// pipeline as before (handlers preserved exactly, only the UI location
// changed).
const MORE_ACTIONS: { label: string; buildQuery: (topic: string) => string }[] = [
  { label: "Explain simpler", buildQuery: (t) => `Explain ${t} more simply` },
  { label: "More detail", buildQuery: (t) => `Give a more detailed explanation of ${t}` },
  { label: "Revision notes", buildQuery: (t) => `Create revision notes for ${t}` },
  { label: "Viva questions", buildQuery: (t) => `Generate viva questions for ${t}` },
  { label: "Exam questions", buildQuery: (t) => `Generate likely exam questions for ${t}` },
  { label: "Short quiz", buildQuery: (t) => `Create a short quiz on ${t}` },
  { label: "Prerequisites", buildQuery: (t) => `Show prerequisites for ${t}` },
  { label: "Related concepts", buildQuery: (t) => `Show related concepts for ${t}` },
  { label: "Compare", buildQuery: (t) => `Compare ${t} with a similar concept` },
];

export default function ResponseActions({
  answerText,
  topic,
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
    const utterance = new SpeechSynthesisUtterance(answerText);
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

  function handleMoreAction(buildQuery: (topic: string) => string) {
    onSelectTopic(buildQuery(topic));
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
              onClick={() => handleMoreAction(action.buildQuery)}
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
