"use client";

import { useCallback, useEffect, useRef, useState } from "react";

// ---------------------------------------------------------------------------
// Thin wrapper around the browser's SpeechRecognition API. No new npm
// dependency — this is a standard browser API (Chrome/Edge as
// webkitSpeechRecognition, not yet standardized everywhere, hence the
// explicit support check and clear error messaging rather than assuming
// it exists).
//
// IMPORTANT: this never auto-submits. It only ever calls onTranscript with
// the recognized text — the caller (ChatInput) is responsible for putting
// it in the input box for the user to review/edit before sending.
// ---------------------------------------------------------------------------

export type VoiceStatus = "idle" | "listening" | "processing" | "error";

interface UseVoiceInputOptions {
  onTranscript: (text: string) => void;
}

interface UseVoiceInputResult {
  status: VoiceStatus;
  error: string | null;
  isSupported: boolean;
  start: () => void;
  stop: () => void;
}

// Minimal ambient typing — the Web Speech API isn't in TS's default DOM
// lib, and adding a package for this alone isn't warranted.
interface MinimalSpeechRecognition extends EventTarget {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  start: () => void;
  stop: () => void;
  onresult: ((event: any) => void) | null;
  onerror: ((event: any) => void) | null;
  onend: (() => void) | null;
}

function getRecognitionConstructor(): (new () => MinimalSpeechRecognition) | null {
  if (typeof window === "undefined") return null;
  const w = window as unknown as Record<string, unknown>;
  return (w.SpeechRecognition || w.webkitSpeechRecognition) as
    | (new () => MinimalSpeechRecognition)
    | undefined
    | null
    || null;
}

export function useVoiceInput({ onTranscript }: UseVoiceInputOptions): UseVoiceInputResult {
  const [status, setStatus] = useState<VoiceStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const recognitionRef = useRef<MinimalSpeechRecognition | null>(null);
  const errorTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isMountedRef = useRef(true);
  // FIX: computing this synchronously (getRecognitionConstructor() !== null)
  // caused a hydration mismatch — on the server, `window` doesn't exist, so
  // this was always false there, but true on the client if the browser
  // supports speech recognition. That made the mic button present in the
  // client's expected markup but absent from the server-rendered HTML,
  // which React reported as mismatched text on the wrong button. Starting
  // at false on both server and the first client render, then flipping to
  // the real value only after mount (client-only, post-hydration), keeps
  // the initial render identical on both sides.
  const [isSupported, setIsSupported] = useState(false);
  useEffect(() => {
    setIsSupported(getRecognitionConstructor() !== null);
  }, []);

  // Clears any pending "revert to idle" timer — called before scheduling a
  // new one and on unmount, so timers can never stack up or fire after the
  // component is gone.
  const clearErrorTimeout = useCallback(() => {
    if (errorTimeoutRef.current !== null) {
      clearTimeout(errorTimeoutRef.current);
      errorTimeoutRef.current = null;
    }
  }, []);

  function scheduleIdleReset() {
    clearErrorTimeout();
    errorTimeoutRef.current = setTimeout(() => {
      errorTimeoutRef.current = null;
      if (isMountedRef.current) setStatus("idle");
    }, 3000);
  }

  // Detaches all handlers and drops the ref so a stale/finishing instance
  // can never call back into React state after we've moved on, and so
  // start() can tell a session is genuinely no longer active.
  function detachRecognition() {
    const recognition = recognitionRef.current;
    if (recognition) {
      recognition.onresult = null;
      recognition.onerror = null;
      recognition.onend = null;
    }
    recognitionRef.current = null;
  }

  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
      clearErrorTimeout();
      recognitionRef.current?.stop();
      detachRecognition();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const start = useCallback(() => {
    // Prevent multiple concurrent recognition sessions — calling .start()
    // on a second instance while one is already active throws in the
    // browser. If a session is already running, this is a no-op.
    if (recognitionRef.current) {
      return;
    }

    const Recognition = getRecognitionConstructor();
    if (!Recognition) {
      setStatus("error");
      setError("Voice input isn't supported in this browser. Try Chrome or Edge.");
      scheduleIdleReset();
      return;
    }

    setError(null);
    const recognition = new Recognition();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = true;

    recognition.onresult = (event: any) => {
      let transcript = "";
      for (let i = 0; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      onTranscript(transcript);
      if (event.results[event.results.length - 1].isFinal) {
        if (isMountedRef.current) setStatus("processing");
      }
    };

    recognition.onerror = (event: any) => {
      detachRecognition();
      if (!isMountedRef.current) return;
      setStatus("error");
      const reason =
        event?.error === "not-allowed" || event?.error === "permission-denied"
          ? "Microphone permission was denied."
          : event?.error === "no-speech"
          ? "No speech detected — try again."
          : "Voice input failed.";
      setError(reason);
      scheduleIdleReset();
    };

    recognition.onend = () => {
      detachRecognition();
      if (!isMountedRef.current) return;
      setStatus((prev) => (prev === "error" ? prev : "idle"));
    };

    recognitionRef.current = recognition;
    recognition.start();
    setStatus("listening");
  }, [onTranscript]);

  const stop = useCallback(() => {
    recognitionRef.current?.stop();
    setStatus("idle");
  }, []);

  return { status, error, isSupported, start, stop };
}
