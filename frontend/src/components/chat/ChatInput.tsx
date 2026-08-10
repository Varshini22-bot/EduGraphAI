"use client";

import { KeyboardEvent, useRef, useState } from "react";
import { useSettings } from "@/context/SettingsContext";
import { useVoiceInput } from "@/lib/useVoiceInput";

interface ChatInputProps {
  onSubmit: (query: string) => void;
  isLoading?: boolean;
  variant?: "hero" | "bar";
  placeholder?: string;
}

const MAX_TEXTAREA_HEIGHT = 160;

export default function ChatInput({
  onSubmit,
  isLoading = false,
  variant = "bar",
  placeholder = "Ask about a topic, or try \"Explain recursion for 8 marks\"...",
}: ChatInputProps) {
  const { settings } = useSettings();
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const [justStopped, setJustStopped] = useState(false);
  const { status: voiceStatus, error: voiceError, isSupported: voiceSupported, start, stop } =
    useVoiceInput({
      onTranscript: (text) => {
        setValue(text);
        requestAnimationFrame(resize);
      },
    });

  function resize() {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, MAX_TEXTAREA_HEIGHT)}px`;
  }

  function submit() {
    const trimmed = value.trim();
    if (!trimmed || isLoading) return;
    onSubmit(trimmed);
    setValue("");
    requestAnimationFrame(() => {
      if (textareaRef.current) textareaRef.current.style.height = "auto";
    });
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (settings.enterToSend) {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        submit();
      }
    } else {
      if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) {
        event.preventDefault();
        submit();
      }
    }
  }

  function handleMicClick() {
    if (voiceStatus === "listening") {
      stop();
      setJustStopped(true);
      setTimeout(() => setJustStopped(false), 1500);
    } else {
      start();
    }
  }

  const voiceLabel =
    voiceStatus === "listening"
      ? "Listening..."
      : voiceStatus === "processing"
      ? "Processing..."
      : voiceError
      ? voiceError
      : justStopped
      ? "Stopped"
      : null;

  return (
    <div>
      <div className="flex items-end gap-1.5 rounded-2xl border border-border-subtle bg-inputbg pr-1.5 transition-colors focus-within:border-teal focus-within:shadow-[0_0_0_3px_rgba(69,214,198,0.14)]">
        <div
          className={`flex flex-1 items-end ${
            variant === "hero" ? "py-2 pl-5" : "py-1.5 pl-4.5"
          }`}
        >
          <label htmlFor="chat-input" className="sr-only">
            Ask the learning assistant a question
          </label>
          <textarea
            id="chat-input"
            ref={textareaRef}
            rows={1}
            value={value}
            onChange={(event) => {
              setValue(event.target.value);
              resize();
            }}
            onKeyDown={handleKeyDown}
            placeholder={
              settings.enterToSend ? placeholder : `${placeholder} (Ctrl+Enter to send)`
            }
            disabled={isLoading}
            className="min-w-0 flex-1 resize-none bg-transparent py-1.5 text-[14.5px] leading-[1.5] text-ink-primary outline-none placeholder:text-ink-tertiary disabled:opacity-60"
            style={{ maxHeight: MAX_TEXTAREA_HEIGHT }}
          />
        </div>

        {voiceSupported && (
          <button
            type="button"
            onClick={handleMicClick}
            disabled={isLoading}
            title={voiceStatus === "listening" ? "Stop listening" : "Ask by voice"}
            aria-label={voiceStatus === "listening" ? "Stop listening" : "Ask by voice"}
            className={`mb-0.5 flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg border text-base transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${
              voiceStatus === "listening"
                ? "border-danger bg-danger-dim text-danger"
                : "border-border-subtle text-ink-secondary hover:border-teal hover:text-teal"
            }`}
          >
            {voiceStatus === "listening" ? "●" : "🎤"}
          </button>
        )}

        <button
          type="button"
          onClick={submit}
          disabled={isLoading || value.trim().length === 0}
          aria-label="Submit question"
          className="mb-0.5 flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg bg-teal text-base font-bold text-[#05221f] transition-transform hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50 disabled:translate-y-0"
        >
          {isLoading ? (
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-[#05221f]/35 border-t-[#05221f]" />
          ) : (
            "→"
          )}
        </button>
      </div>

      {voiceLabel && (
        <div
          className={`mt-1.5 px-1 text-[11.5px] ${
            voiceError ? "text-danger" : "text-ink-tertiary"
          }`}
        >
          {voiceLabel}
        </div>
      )}
    </div>
  );
}
