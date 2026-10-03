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
  onShare?: () => void;
}

function isSpeechSynthesisSupported(): boolean {
  return typeof window !== "undefined" && "speechSynthesis" in window;
}

function cleanTextForSpeech(text: string): string {
  return text
    .replace(/^[ \t]*([-*_=])(?:[ \t]*\1){2,}[ \t]*$/gm, "\n")
    .replace(/^[ \t]*#{1,6}[ \t]+/gm, "")
    .replace(/^[ \t]*[-*+•][ \t]+/gm, "")
    .replace(/^[ \t]*>[ \t]?/gm, "")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/[`*_]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

// Primary educational action chips (Phase 4)
const PRIMARY_EDUCATIONAL_ACTIONS: { label: string; action: ContextualAction; icon: string }[] = [
  { label: "Explain Simply", action: "explain_simpler", icon: "💡" },
  { label: "Short Answer (2M)", action: "short_answer", icon: "📝" },
  { label: "5-Mark Answer", action: "five_mark_answer", icon: "⭐" },
  { label: "10-Mark Answer", action: "ten_mark_answer", icon: "🎯" },
  { label: "Give Example", action: "give_example", icon: "🔍" },
  { label: "Related Concepts", action: "related_concepts", icon: "🕸️" },
];

// Additional actions in overflow menu
const OVERFLOW_ACTIONS: { label: string; action: ContextualAction }[] = [
  { label: "More detail", action: "more_detail" },
  { label: "Revision notes", action: "revision_notes" },
  { label: "Viva questions", action: "viva_questions" },
  { label: "Exam questions", action: "exam_questions" },
  { label: "Prerequisites", action: "prerequisites" },
  { label: "Compare with similar topic", action: "compare" },
];

const FEEDBACK_REASONS = [
  "Inaccurate or factually incorrect",
  "Irrelevant to question or subject",
  "Incomplete explanation",
  "Too complicated / hard to follow",
  "Missing exam points or diagram",
  "Other",
];

export default function ResponseActions({
  answerText,
  topic,
  originalQuery,
  isBookmarked,
  onToggleBookmark,
  onRegenerate,
  onSelectTopic,
  onShare,
}: ResponseActionsProps) {
  const [copied, setCopied] = useState(false);
  const [speechState, setSpeechState] = useState<SpeechState>("idle");
  const [speechError, setSpeechError] = useState<string | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);

  // User feedback state: helpful | unhelpful | null
  const [feedback, setFeedback] = useState<"helpful" | "unhelpful" | null>(null);
  const [feedbackModalOpen, setFeedbackModalOpen] = useState(false);
  const [selectedReason, setSelectedReason] = useState<string>(FEEDBACK_REASONS[0]);
  const [feedbackNotes, setFeedbackNotes] = useState("");
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const menuButtonRef = useRef<HTMLButtonElement>(null);

  // Stop any speech if this message unmounts
  useEffect(() => {
    return () => {
      if (isSpeechSynthesisSupported()) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  // Close the More menu on outside click and on Escape
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

  function handleActionClick(action: ContextualAction) {
    onSelectTopic(buildContextualActionQuery(topic, action, originalQuery));
    setMenuOpen(false);
  }

  function handleHelpful() {
    if (feedback === "helpful") {
      setFeedback(null);
    } else {
      setFeedback("helpful");
      try {
        const stored = JSON.parse(localStorage.getItem("edugraph_feedback") || "[]");
        stored.push({ topic, feedback: "helpful", timestamp: Date.now() });
        localStorage.setItem("edugraph_feedback", JSON.stringify(stored.slice(-50)));
      } catch {
        // Ignore localStorage errors
      }
    }
  }

  function handleUnhelpfulClick() {
    if (feedback === "unhelpful") {
      setFeedback(null);
    } else {
      setFeedback("unhelpful");
      setFeedbackModalOpen(true);
      setFeedbackSubmitted(false);
    }
  }

  function submitFeedback() {
    setFeedbackSubmitted(true);
    try {
      const stored = JSON.parse(localStorage.getItem("edugraph_feedback") || "[]");
      stored.push({
        topic,
        feedback: "unhelpful",
        reason: selectedReason,
        notes: feedbackNotes,
        timestamp: Date.now(),
      });
      localStorage.setItem("edugraph_feedback", JSON.stringify(stored.slice(-50)));
    } catch {
      // Ignore localStorage errors
    }
    setTimeout(() => {
      setFeedbackModalOpen(false);
    }, 1200);
  }

  return (
    <div className="flex flex-col gap-2.5 pt-1">
      {/* Primary Toolbar */}
      <div className="relative flex flex-wrap items-center gap-1">
        {/* Copy Button */}
        <button
          onClick={handleCopy}
          title="Copy answer"
          aria-label="Copy answer"
          className="flex items-center gap-1 rounded-md px-2 py-1 text-[11.5px] text-ink-tertiary transition-colors hover:bg-hoverbg hover:text-ink-primary"
        >
          {copied ? "✓" : "⧉"}{" "}
          <span className="hidden sm:inline">{copied ? "Copied" : "Copy"}</span>
        </button>

        {/* Regenerate Button */}
        <button
          onClick={onRegenerate}
          title="Regenerate answer"
          aria-label="Regenerate answer"
          className="flex items-center gap-1 rounded-md px-2 py-1 text-[11.5px] text-ink-tertiary transition-colors hover:bg-hoverbg hover:text-ink-primary"
        >
          ↻ <span className="hidden sm:inline">Regenerate</span>
        </button>

        {/* Share Button (Phase 1 / Share UX) */}
        {onShare && (
          <button
            onClick={onShare}
            title="Share this conversation"
            aria-label="Share this conversation"
            className="flex items-center gap-1 rounded-md px-2 py-1 text-[11.5px] text-ink-tertiary transition-colors hover:bg-hoverbg hover:text-ink-primary"
          >
            🔗 <span className="hidden sm:inline">Share</span>
          </button>
        )}

        {/* Bookmark Button */}
        <button
          onClick={onToggleBookmark}
          title={isBookmarked ? "Remove bookmark" : "Bookmark this answer"}
          aria-label={isBookmarked ? "Remove bookmark" : "Bookmark this answer"}
          aria-pressed={isBookmarked}
          className={`flex items-center gap-1 rounded-md px-2 py-1 text-[11.5px] transition-colors hover:bg-hoverbg ${
            isBookmarked ? "text-amber" : "text-ink-tertiary hover:text-ink-primary"
          }`}
        >
          {isBookmarked ? "★" : "☆"}{" "}
          <span className="hidden sm:inline">{isBookmarked ? "Saved" : "Bookmark"}</span>
        </button>

        {/* Feedback: Helpful */}
        <button
          onClick={handleHelpful}
          title="Mark answer as helpful"
          aria-label="Helpful"
          aria-pressed={feedback === "helpful"}
          className={`flex items-center gap-1 rounded-md px-2 py-1 text-[11.5px] transition-colors hover:bg-hoverbg ${
            feedback === "helpful"
              ? "bg-teal-dim font-medium text-teal"
              : "text-ink-tertiary hover:text-ink-primary"
          }`}
        >
          👍 <span className="hidden sm:inline">Helpful</span>
        </button>

        {/* Feedback: Not Helpful */}
        <button
          onClick={handleUnhelpfulClick}
          title="Mark answer as not helpful"
          aria-label="Not helpful"
          aria-pressed={feedback === "unhelpful"}
          className={`flex items-center gap-1 rounded-md px-2 py-1 text-[11.5px] transition-colors hover:bg-hoverbg ${
            feedback === "unhelpful"
              ? "bg-danger-dim font-medium text-danger"
              : "text-ink-tertiary hover:text-ink-primary"
          }`}
        >
          👎 <span className="hidden sm:inline">Not helpful</span>
        </button>

        {/* TTS / Read aloud */}
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

        {/* Overflow Menu */}
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
            className="absolute right-0 top-full z-20 mt-1 w-56 overflow-hidden rounded-lg border border-border-subtle bg-elevated py-1 shadow-elevated animate-fadein"
          >
            {OVERFLOW_ACTIONS.map((item) => (
              <button
                key={item.label}
                role="menuitem"
                onClick={() => handleActionClick(item.action)}
                className="block w-full px-3 py-2 text-left text-[12.5px] text-ink-secondary transition-colors hover:bg-hoverbg hover:text-ink-primary"
              >
                {item.label}
              </button>
            ))}
          </div>
        )}

        {speechError && <span className="text-[11px] text-danger">{speechError}</span>}
      </div>

      {/* Phase 4 Educational Action Chips */}
      <div className="flex flex-wrap items-center gap-1.5 pt-0.5">
        <span className="text-[11px] font-semibold uppercase tracking-wider text-ink-tertiary mr-1">
          Study Actions:
        </span>
        {PRIMARY_EDUCATIONAL_ACTIONS.map((btn) => (
          <button
            key={btn.action}
            onClick={() => handleActionClick(btn.action)}
            className="inline-flex items-center gap-1.5 rounded-full border border-border-subtle bg-elevated/70 px-2.5 py-1 text-[11.5px] font-medium text-ink-secondary transition-all hover:border-teal hover:bg-teal-dim/20 hover:text-ink-primary hover:-translate-y-0.5"
          >
            <span>{btn.icon}</span>
            <span>{btn.label}</span>
          </button>
        ))}
      </div>

      {/* Feedback modal for thumbs down */}
      {feedbackModalOpen && (
        <div
          className="fixed inset-0 z-[160] flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm animate-fadein"
          onClick={() => setFeedbackModalOpen(false)}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="feedback-dialog-title"
            onClick={(e) => e.stopPropagation()}
            className="card w-full max-w-[420px] p-5 shadow-elevated focus:outline-none"
          >
            <div className="flex items-center justify-between border-b border-border-subtle pb-3">
              <h3 id="feedback-dialog-title" className="text-[15px] font-semibold text-ink-primary">
                Help us improve this answer
              </h3>
              <button
                onClick={() => setFeedbackModalOpen(false)}
                className="rounded p-1 text-ink-tertiary hover:text-ink-primary"
                aria-label="Close"
              >
                ✕
              </button>
            </div>

            {feedbackSubmitted ? (
              <div className="py-6 text-center">
                <span className="text-2xl">✓</span>
                <p className="mt-2 text-[14px] font-medium text-teal">
                  Thank you for your feedback!
                </p>
                <p className="mt-1 text-[12px] text-ink-tertiary">
                  We use this to refine educational knowledge graph alignment.
                </p>
              </div>
            ) : (
              <div className="mt-3 flex flex-col gap-3">
                <p className="text-[12.5px] text-ink-secondary">
                  What was the issue with the answer for <strong className="text-ink-primary">{topic}</strong>?
                </p>
                <div className="flex flex-col gap-1.5">
                  {FEEDBACK_REASONS.map((reason) => (
                    <label
                      key={reason}
                      className="flex cursor-pointer items-center gap-2 rounded-md p-1.5 text-[12.5px] text-ink-secondary hover:bg-hoverbg"
                    >
                      <input
                        type="radio"
                        name="feedbackReason"
                        checked={selectedReason === reason}
                        onChange={() => setSelectedReason(reason)}
                        className="accent-teal"
                      />
                      <span>{reason}</span>
                    </label>
                  ))}
                </div>

                <textarea
                  value={feedbackNotes}
                  onChange={(e) => setFeedbackNotes(e.target.value)}
                  placeholder="Optional details or corrections..."
                  rows={2}
                  className="w-full resize-none rounded-md border border-border-subtle bg-inputbg p-2 text-[12.5px] text-ink-primary outline-none focus:border-teal"
                />

                <div className="mt-2 flex items-center justify-end gap-2">
                  <button
                    onClick={() => setFeedbackModalOpen(false)}
                    className="btn-ghost !px-3 !py-1.5 text-[12.5px]"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={submitFeedback}
                    className="btn-primary !px-4 !py-1.5 text-[12.5px]"
                  >
                    Submit Feedback
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
