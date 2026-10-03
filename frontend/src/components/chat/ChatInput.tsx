"use client";

import { KeyboardEvent, useEffect, useRef, useState } from "react";
import { useSettings } from "@/context/SettingsContext";
import { useVoiceInput } from "@/lib/useVoiceInput";

export interface SubjectOption {
  id: string | null;
  label: string;
  icon: string;
  badge: string;
}

export const AVAILABLE_SUBJECTS: SubjectOption[] = [
  { id: null, label: "All Subjects", icon: "📚", badge: "All" },
  { id: "DSA", label: "Data Structures & Algorithms", icon: "🌲", badge: "DSA" },
  { id: "ADA", label: "Analysis & Design of Algorithms", icon: "⚡", badge: "ADA" },
  { id: "CN", label: "Computer Networks", icon: "🌐", badge: "CN" },
  { id: "ML", label: "Machine Learning", icon: "🤖", badge: "ML" },
  { id: "OS", label: "Operating Systems", icon: "💻", badge: "OS" },
  { id: "SEPM", label: "Software Engineering & PM", icon: "📊", badge: "SEPM" },
];

interface ChatInputProps {
  onSubmit: (query: string, subject?: string | null) => void;
  isLoading?: boolean;
  onStopGenerating?: () => void;
  selectedSubject?: string | null;
  onSelectSubject?: (subject: string | null) => void;
  initialValue?: string;
  onClearInitialValue?: () => void;
  variant?: "hero" | "bar";
  placeholder?: string;
}

const MAX_TEXTAREA_HEIGHT = 160;

export default function ChatInput({
  onSubmit,
  isLoading = false,
  onStopGenerating,
  selectedSubject = null,
  onSelectSubject,
  initialValue = "",
  onClearInitialValue,
  variant = "bar",
  placeholder = "Ask EduGraphAI about concepts, algorithms, or exam questions...",
}: ChatInputProps) {
  const { settings } = useSettings();
  const [value, setValue] = useState(initialValue);
  const [subjectDropdownOpen, setSubjectDropdownOpen] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const subjectDropdownRef = useRef<HTMLDivElement>(null);

  const [justStopped, setJustStopped] = useState(false);
  const { status: voiceStatus, error: voiceError, isSupported: voiceSupported, start, stop } =
    useVoiceInput({
      onTranscript: (text) => {
        setValue((prev) => (prev ? `${prev} ${text}` : text));
        requestAnimationFrame(resize);
      },
    });

  // Sync initialValue when editing a query
  useEffect(() => {
    if (initialValue) {
      setValue(initialValue);
      requestAnimationFrame(() => {
        resize();
        textareaRef.current?.focus();
        textareaRef.current?.setSelectionRange(initialValue.length, initialValue.length);
      });
      onClearInitialValue?.();
    }
  }, [initialValue, onClearInitialValue]);

  // Click outside to close subject dropdown
  useEffect(() => {
    if (!subjectDropdownOpen) return;

    function handleClickOutside(e: MouseEvent | TouchEvent) {
      if (
        subjectDropdownRef.current &&
        !subjectDropdownRef.current.contains(e.target as Node)
      ) {
        setSubjectDropdownOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("touchstart", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("touchstart", handleClickOutside);
    };
  }, [subjectDropdownOpen]);

  function resize() {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, MAX_TEXTAREA_HEIGHT)}px`;
  }

  function submit() {
    const trimmed = value.trim();
    if (!trimmed || isLoading) return;
    onSubmit(trimmed, selectedSubject);
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

  const currentSubjectObj =
    AVAILABLE_SUBJECTS.find((s) => s.id === selectedSubject) || AVAILABLE_SUBJECTS[0];

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
    <div className="relative w-full">
      <div className="flex flex-col rounded-2xl border border-border-subtle bg-inputbg transition-all focus-within:border-teal focus-within:shadow-[0_0_0_3px_rgba(69,214,198,0.14)]">
        {/* Top: Textarea input */}
        <div className={`flex items-start px-4 pt-3 ${variant === "hero" ? "pb-1" : "pb-1"}`}>
          <label htmlFor="chat-input" className="sr-only">
            Ask EduGraphAI an educational question
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
              settings.enterToSend
                ? placeholder
                : `${placeholder} (Ctrl+Enter to send, Shift+Enter for newline)`
            }
            disabled={isLoading}
            className="min-w-0 flex-1 resize-none bg-transparent text-[14.5px] leading-[1.55] text-ink-primary outline-none placeholder:text-ink-tertiary disabled:opacity-60"
            style={{ maxHeight: MAX_TEXTAREA_HEIGHT }}
          />
        </div>

        {/* Bottom toolbar inside input box */}
        <div className="flex flex-wrap items-center justify-between gap-2 px-3 pb-2.5 pt-1 border-t border-border-subtle/40">
          {/* Left: Subject Selector Dropdown Pill */}
          <div className="relative" ref={subjectDropdownRef}>
            <button
              type="button"
              disabled={isLoading}
              onClick={() => setSubjectDropdownOpen((v) => !v)}
              className="flex items-center gap-1.5 rounded-full border border-border-subtle bg-elevated/70 px-2.5 py-1 text-[12px] font-medium text-ink-secondary transition-colors hover:border-teal hover:text-ink-primary disabled:opacity-50"
              title="Filter by subject syllabus"
              aria-label="Select subject"
              aria-haspopup="listbox"
              aria-expanded={subjectDropdownOpen}
            >
              <span>{currentSubjectObj.icon}</span>
              <span className="font-semibold text-teal">{currentSubjectObj.badge}</span>
              <span className="text-[10px] text-ink-tertiary">▼</span>
            </button>

            {subjectDropdownOpen && (
              <div
                role="listbox"
                className="absolute bottom-full left-0 z-30 mb-1.5 w-60 overflow-hidden rounded-xl border border-border-subtle bg-elevated py-1 shadow-elevated animate-fadein"
              >
                <div className="border-b border-border-subtle/60 px-3 py-1.5 text-[10.5px] font-semibold uppercase tracking-wider text-ink-tertiary">
                  Knowledge Graph Syllabus
                </div>
                {AVAILABLE_SUBJECTS.map((sub) => {
                  const isSelected = sub.id === selectedSubject;
                  return (
                    <button
                      key={sub.label}
                      type="button"
                      role="option"
                      aria-selected={isSelected}
                      onClick={() => {
                        onSelectSubject?.(sub.id);
                        setSubjectDropdownOpen(false);
                      }}
                      className={`flex w-full items-center justify-between px-3 py-2 text-left text-[12.5px] transition-colors hover:bg-hoverbg ${
                        isSelected
                          ? "bg-teal-dim/30 font-semibold text-teal"
                          : "text-ink-secondary hover:text-ink-primary"
                      }`}
                    >
                      <span className="flex items-center gap-2">
                        <span>{sub.icon}</span>
                        <span>{sub.badge}</span>
                      </span>
                      {isSelected && <span className="text-teal">✓</span>}
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Right: Voice Input + Stop / Send Buttons */}
          <div className="flex items-center gap-1.5">
            {voiceSupported && (
              <button
                type="button"
                onClick={handleMicClick}
                disabled={isLoading}
                title={voiceStatus === "listening" ? "Stop listening" : "Ask by voice"}
                aria-label={voiceStatus === "listening" ? "Stop listening" : "Ask by voice"}
                className={`flex h-8 w-8 items-center justify-center rounded-lg border text-sm transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${
                  voiceStatus === "listening"
                    ? "border-danger bg-danger-dim text-danger"
                    : "border-border-subtle text-ink-secondary hover:border-teal hover:text-teal"
                }`}
              >
                {voiceStatus === "listening" ? "●" : "🎤"}
              </button>
            )}

            {/* Stop generating button when loading */}
            {isLoading && onStopGenerating ? (
              <button
                type="button"
                onClick={onStopGenerating}
                aria-label="Stop generating response"
                className="flex items-center gap-1.5 rounded-lg border border-danger/60 bg-danger-dim px-3 py-1.5 text-[12px] font-semibold text-danger transition-transform hover:scale-105"
              >
                <span className="h-2 w-2 rounded-sm bg-danger" />
                <span>Stop generating</span>
              </button>
            ) : (
              /* Send button */
              <button
                type="button"
                onClick={submit}
                disabled={isLoading || value.trim().length === 0}
                aria-label="Submit question"
                className="flex h-8 w-8 items-center justify-center rounded-lg bg-teal text-sm font-bold text-[#05221f] transition-transform hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-40 disabled:translate-y-0"
              >
                →
              </button>
            )}
          </div>
        </div>
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
