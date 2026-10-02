"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Conversation } from "@/lib/types";
import {
  copyShareLink,
  createShareLink,
  isNativeShareSupported,
  prepareShareData,
  triggerNativeShare,
} from "@/lib/share";
import { useToast } from "@/context/ToastContext";

interface ShareDialogProps {
  isOpen: boolean;
  onClose: () => void;
  conversation: Conversation | null;
}

function CopyIcon({ className }: { className?: string }) {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className={className ?? "flex-shrink-0"}
    >
      <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
    </svg>
  );
}

function CheckIcon({ className }: { className?: string }) {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.4"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className={className ?? "flex-shrink-0"}
    >
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

function NativeShareIcon({ className }: { className?: string }) {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className={className ?? "flex-shrink-0"}
    >
      <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8" />
      <polyline points="16 6 12 2 8 6" />
      <line x1="12" y1="2" x2="12" y2="15" />
    </svg>
  );
}

export default function ShareDialog({
  isOpen,
  onClose,
  conversation,
}: ShareDialogProps) {
  const [copied, setCopied] = useState(false);
  const [shareUrl, setShareUrl] = useState<string>("");
  const [isOversized, setIsOversized] = useState(false);
  const [oversizedMessage, setOversizedMessage] = useState<string>("");
  const [isEncoding, setIsEncoding] = useState(false);

  const { showToast } = useToast();
  const dialogRef = useRef<HTMLDivElement>(null);
  const copyTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const shareData = useMemo(() => prepareShareData(conversation), [conversation]);
  const hasNativeShare = useMemo(() => isNativeShareSupported(), []);

  // Generate frontend snapshot URL when dialog opens or conversation changes
  useEffect(() => {
    if (!isOpen) return;

    if (!shareData.preview.hasContent) {
      setShareUrl(shareData.url);
      setIsOversized(false);
      setOversizedMessage("");
      return;
    }

    let isMounted = true;
    setIsEncoding(true);

    createShareLink(conversation)
      .then((res) => {
        if (!isMounted) return;
        setIsEncoding(false);
        if (res.isOversized) {
          setIsOversized(true);
          setOversizedMessage(
            res.errorMessage ||
              "This conversation is too large to share as a link. Start a shorter conversation or copy the important part manually."
          );
          setShareUrl("");
        } else {
          setIsOversized(false);
          setOversizedMessage("");
          setShareUrl(res.url);
        }
      })
      .catch(() => {
        if (!isMounted) return;
        setIsEncoding(false);
        setShareUrl(shareData.url);
      });

    return () => {
      isMounted = false;
    };
  }, [isOpen, conversation, shareData]);

  // Keyboard accessibility: ESC closes modal
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        onClose();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  // Clean up copy timeout when modal unmounts or closes
  useEffect(() => {
    if (!isOpen) {
      setCopied(false);
      if (copyTimeoutRef.current) {
        clearTimeout(copyTimeoutRef.current);
      }
    }
  }, [isOpen]);

  // Focus trap / initial focus on modal open
  useEffect(() => {
    if (isOpen && dialogRef.current) {
      dialogRef.current.focus();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  async function handleCopy() {
    if (isOversized) {
      showToast(oversizedMessage, "danger");
      return;
    }

    const targetUrl = shareUrl || shareData.url;
    const success = await copyShareLink(targetUrl);
    if (success) {
      setCopied(true);
      showToast("Link copied to clipboard!");
      if (copyTimeoutRef.current) clearTimeout(copyTimeoutRef.current);
      copyTimeoutRef.current = setTimeout(() => {
        setCopied(false);
      }, 2400);
    } else {
      showToast("Unable to copy link to clipboard.", "danger");
    }
  }

  async function handleNativeShare() {
    if (isOversized) {
      showToast(oversizedMessage, "danger");
      return;
    }

    const targetUrl = shareUrl || shareData.url;
    const result = await triggerNativeShare({
      title: shareData.title,
      text: shareData.text,
      url: targetUrl,
    });

    if (result === "shared") {
      showToast("Conversation shared successfully!");
    } else if (result === "error") {
      showToast("Unable to open device share sheet.", "danger");
    }
    // "aborted" (user dismissed native sheet) is handled silently
  }

  const { preview } = shareData;

  return (
    <div
      className="fixed inset-0 z-[150] flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm animate-fadein"
      onClick={onClose}
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="share-dialog-title"
        aria-describedby="share-dialog-desc"
        tabIndex={-1}
        onClick={(e) => e.stopPropagation()}
        className="card w-full max-w-[480px] p-5 sm:p-6 shadow-elevated focus:outline-none"
      >
        {/* Header */}
        <div className="flex items-start justify-between gap-3 border-b border-border-subtle pb-3.5">
          <div className="min-w-0">
            <h2
              id="share-dialog-title"
              className="text-[17px] font-semibold text-ink-primary"
            >
              Share conversation
            </h2>
            <p
              id="share-dialog-desc"
              className="mt-0.5 text-[13px] text-ink-secondary"
            >
              Share a snapshot of this conversation with others.
            </p>
          </div>
          <button
            onClick={onClose}
            aria-label="Close dialog"
            title="Close"
            className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-md text-ink-tertiary transition-colors hover:bg-hoverbg hover:text-ink-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal/50"
          >
            ✕
          </button>
        </div>

        {/* Conversation Preview Area */}
        {preview.hasContent ? (
          <div className="my-4 space-y-2.5 rounded-lg border border-border-subtle bg-elevated/70 p-3.5">
            <div className="flex items-center justify-between gap-2 text-[11px] font-medium text-ink-tertiary">
              <span className="uppercase tracking-wider">Conversation Preview</span>
              {preview.topic && (
                <span className="truncate rounded bg-teal-dim/80 px-2 py-0.5 text-[11px] font-semibold text-teal">
                  {preview.topic}
                </span>
              )}
            </div>

            {/* First user question */}
            {preview.firstQuestion && (
              <div className="flex items-start gap-2 text-[13px]">
                <span
                  aria-hidden="true"
                  className="mt-0.5 flex h-4 w-4 flex-shrink-0 items-center justify-center rounded-full border border-border-subtle bg-surface text-[10px] font-semibold text-teal"
                >
                  Q
                </span>
                <span className="line-clamp-2 font-medium leading-snug text-ink-primary">
                  {preview.firstQuestion}
                </span>
              </div>
            )}

            {/* Assistant response preview */}
            {preview.firstAnswerPreview && (
              <div className="flex items-start gap-2 border-t border-border-subtle/50 pt-2 text-[12.5px] leading-relaxed text-ink-secondary">
                <span
                  aria-hidden="true"
                  className="mt-0.5 flex h-4 w-4 flex-shrink-0 items-center justify-center rounded-full border border-border-subtle bg-surface text-[10px] font-semibold text-violet"
                >
                  A
                </span>
                <span className="line-clamp-3 flex-1">
                  {preview.firstAnswerPreview}
                </span>
              </div>
            )}

            {preview.messageCount > 1 && (
              <div className="pt-0.5 text-[11.5px] text-ink-tertiary">
                +{preview.messageCount - 1} more{" "}
                {preview.messageCount - 1 === 1 ? "message" : "messages"} in
                conversation
              </div>
            )}
          </div>
        ) : (
          <div className="my-4 flex flex-col items-center justify-center rounded-lg border border-dashed border-border-subtle bg-elevated/40 px-4 py-8 text-center">
            <span className="mb-2 text-2xl" aria-hidden="true">
              💬
            </span>
            <p className="text-[13.5px] font-medium text-ink-secondary">
              Start a conversation to share it.
            </p>
            <p className="mt-1 max-w-[280px] text-[12px] text-ink-tertiary">
              Ask an academic question or explore a concept to see your
              conversation preview here.
            </p>
          </div>
        )}

        {/* Oversized Warning */}
        {isOversized && (
          <div className="mb-3.5 flex items-start gap-2.5 rounded-lg border border-amber/40 bg-amber-dim/50 p-3 text-[12.5px] text-ink-primary">
            <span className="flex-shrink-0 text-amber" aria-hidden="true">
              ⚠
            </span>
            <span className="leading-snug">{oversizedMessage}</span>
          </div>
        )}

        {/* Link field + Copy button */}
        <div className="space-y-1.5">
          <label className="text-[11.5px] font-semibold uppercase tracking-wider text-ink-tertiary">
            Link
          </label>
          <div className="flex items-center gap-2">
            <input
              type="text"
              readOnly
              value={
                isEncoding
                  ? "Generating link…"
                  : isOversized
                  ? "Conversation too large for link sharing"
                  : shareUrl || shareData.url
              }
              aria-label="Share link URL"
              className={`flex-1 min-w-0 truncate rounded-md border border-border-subtle bg-inputbg px-3 py-2 text-[12.5px] outline-none select-all focus:border-teal ${
                isOversized ? "text-ink-tertiary italic" : "text-ink-primary"
              }`}
            />
            <button
              onClick={handleCopy}
              disabled={isEncoding || isOversized || !preview.hasContent}
              className={`btn-primary !px-3.5 !py-2 text-[13px] flex-shrink-0 gap-1.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed ${
                copied ? "!bg-teal !text-surface font-semibold" : ""
              }`}
            >
              {copied ? (
                <>
                  <CheckIcon className="h-3.5 w-3.5 text-surface" />
                  <span>Link copied</span>
                </>
              ) : (
                <>
                  <CopyIcon className="h-3.5 w-3.5" />
                  <span>Copy link</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-5 flex items-center justify-between border-t border-border-subtle pt-3.5">
          {hasNativeShare && !isOversized && preview.hasContent ? (
            <button
              onClick={handleNativeShare}
              disabled={isEncoding}
              className="btn-ghost !px-3 !py-1.5 text-[12.5px] gap-1.5 text-ink-secondary hover:text-ink-primary"
              title="Open native share sheet"
            >
              <NativeShareIcon className="h-3.5 w-3.5" />
              <span>Share…</span>
            </button>
          ) : (
            <div />
          )}

          <button
            onClick={onClose}
            className="btn-ghost !px-4 !py-1.5 text-[13px]"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
