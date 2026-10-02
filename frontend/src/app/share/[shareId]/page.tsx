"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { copyShareLink, decodeConversationSnapshot } from "@/lib/share";
import { fetchSharedConversation } from "@/lib/api";
import { SharedMessage, SharedSnapshotData } from "@/lib/types";

// ---------------------------------------------------------------------------
// Markdown-lite rendering helpers (consistent with AnswerCard)
// ---------------------------------------------------------------------------

function renderInline(text: string, keyPrefix: string) {
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={`${keyPrefix}-${i}`} className="font-semibold text-ink-primary">
          {part.slice(2, -2)}
        </strong>
      );
    }
    if (part.startsWith("`") && part.endsWith("`") && part.length > 1) {
      return (
        <code
          key={`${keyPrefix}-${i}`}
          className="rounded bg-elevated px-1.5 py-0.5 font-mono text-[12.5px] text-teal"
        >
          {part.slice(1, -1)}
        </code>
      );
    }
    return <span key={`${keyPrefix}-${i}`}>{part}</span>;
  });
}

function CodeBlock({ code, language }: { code: string; language: string }) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Ignore clipboard error
    }
  }

  return (
    <div className="my-2.5 overflow-hidden rounded-lg border border-border-subtle bg-base">
      <div className="flex items-center justify-between border-b border-border-subtle bg-elevated px-3 py-1.5">
        <span className="font-mono text-[11px] text-ink-tertiary">
          {language || "code"}
        </span>
        <button
          onClick={handleCopy}
          className="text-[11px] font-medium text-ink-tertiary transition-colors hover:text-ink-primary"
        >
          {copied ? "✓ Copied" : "⧉ Copy"}
        </button>
      </div>
      <pre className="overflow-x-auto p-3 text-[12.5px] leading-[1.6]">
        <code className="font-mono text-ink-primary/90">{code}</code>
      </pre>
    </div>
  );
}

function Table({ headers, rows }: { headers: string[]; rows: string[][] }) {
  return (
    <div className="my-2.5 overflow-x-auto rounded-lg border border-border-subtle">
      <table className="w-full border-collapse text-left text-[13px]">
        <thead>
          <tr className="border-b border-border-subtle bg-elevated">
            {headers.map((h, i) => (
              <th key={i} className="px-3 py-2 font-semibold text-ink-primary">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, ri) => (
            <tr key={ri} className={ri % 2 === 1 ? "bg-elevated/40" : ""}>
              {row.map((cell, ci) => (
                <td
                  key={ci}
                  className="border-t border-border-subtle px-3 py-2 text-ink-primary/90"
                >
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function isTableRow(line: string): boolean {
  return line.trim().startsWith("|") && line.trim().endsWith("|");
}

function isTableDivider(line: string): boolean {
  return /^\|?[\s:|-]+\|?$/.test(line.trim()) && line.includes("-");
}

function splitTableRow(line: string): string[] {
  return line
    .trim()
    .replace(/^\|/, "")
    .replace(/\|$/, "")
    .split("|")
    .map((cell) => cell.trim());
}

function parseMarkdownBlocks(text: string): JSX.Element[] {
  const lines = text.split("\n");
  const blocks: JSX.Element[] = [];
  let bulletBuffer: string[] = [];
  let numberedBuffer: string[] = [];

  function flushBullets(keyBase: string) {
    if (bulletBuffer.length === 0) return;
    blocks.push(
      <ul key={`ul-${keyBase}`} className="my-1.5 list-disc space-y-1 pl-5">
        {bulletBuffer.map((item, i) => (
          <li key={i} className="text-[14px] leading-[1.7] text-ink-primary/90">
            {renderInline(item, `ul-${keyBase}-${i}`)}
          </li>
        ))}
      </ul>
    );
    bulletBuffer = [];
  }

  function flushNumbered(keyBase: string) {
    if (numberedBuffer.length === 0) return;
    blocks.push(
      <ol key={`ol-${keyBase}`} className="my-1.5 list-decimal space-y-1 pl-5">
        {numberedBuffer.map((item, i) => (
          <li key={i} className="text-[14px] leading-[1.7] text-ink-primary/90">
            {renderInline(item, `ol-${keyBase}-${i}`)}
          </li>
        ))}
      </ol>
    );
    numberedBuffer = [];
  }

  let i = 0;
  while (i < lines.length) {
    const rawLine = lines[i];
    const line = rawLine.trim();

    if (line.length === 0) {
      flushBullets(String(i));
      flushNumbered(String(i));
      i++;
      continue;
    }

    // Fenced code block
    const fenceMatch = line.match(/^```(\w*)\s*$/);
    if (fenceMatch) {
      flushBullets(String(i));
      flushNumbered(String(i));
      const language = fenceMatch[1];
      const codeLines: string[] = [];
      i++;
      while (i < lines.length && !/^```\s*$/.test(lines[i].trim())) {
        codeLines.push(lines[i]);
        i++;
      }
      i++; // skip closing fence
      blocks.push(
        <CodeBlock
          key={`code-${i}`}
          code={codeLines.join("\n")}
          language={language}
        />
      );
      continue;
    }

    // Markdown table
    if (isTableRow(line) && i + 1 < lines.length && isTableDivider(lines[i + 1])) {
      flushBullets(String(i));
      flushNumbered(String(i));
      const headers = splitTableRow(line);
      const rows: string[][] = [];
      i += 2;
      while (i < lines.length && isTableRow(lines[i])) {
        rows.push(splitTableRow(lines[i]));
        i++;
      }
      blocks.push(<Table key={`table-${i}`} headers={headers} rows={rows} />);
      continue;
    }

    // Heading
    const headingMatch = line.match(/^#{2,4}\s+(.*)$/);
    if (headingMatch) {
      flushBullets(String(i));
      flushNumbered(String(i));
      blocks.push(
        <h3
          key={`h-${i}`}
          className="mt-3 text-[15px] font-semibold text-ink-primary"
        >
          {renderInline(headingMatch[1], `h-${i}`)}
        </h3>
      );
      i++;
      continue;
    }

    // Bullet item
    const bulletMatch = line.match(/^[-*•]\s+(.*)$/);
    if (bulletMatch) {
      flushNumbered(String(i));
      bulletBuffer.push(bulletMatch[1]);
      i++;
      continue;
    }

    // Numbered item
    const numberedMatch = line.match(/^\d+[.)]\s+(.*)$/);
    if (numberedMatch) {
      flushBullets(String(i));
      numberedBuffer.push(numberedMatch[1]);
      i++;
      continue;
    }

    // Standard paragraph
    flushBullets(String(i));
    flushNumbered(String(i));
    blocks.push(
      <p
        key={`p-${i}`}
        className="text-[14px] leading-[1.75] text-ink-primary/90"
      >
        {renderInline(line, `p-${i}`)}
      </p>
    );
    i++;
  }

  flushBullets("end");
  flushNumbered("end");

  return blocks;
}

export default function SharedConversationPage() {
  const params = useParams();
  const shareId = typeof params?.shareId === "string" ? params.shareId : "";

  const [snapshot, setSnapshot] = useState<SharedSnapshotData | null>(null);
  const [loading, setLoading] = useState(true);
  const [linkCopied, setLinkCopied] = useState(false);

  useEffect(() => {
    if (!shareId) {
      setLoading(false);
      return;
    }

    let isMounted = true;
    setLoading(true);

    async function loadSharedSnapshot() {
      // 1. If it's a client-compressed legacy token (starts with df. or b64.)
      if (shareId.startsWith("df.") || shareId.startsWith("b64.")) {
        const clientData = await decodeConversationSnapshot(shareId);
        if (isMounted) {
          setSnapshot(clientData);
          setLoading(false);
        }
        return;
      }

      // 2. Otherwise fetch the persistent snapshot from backend
      try {
        const serverData = await fetchSharedConversation(shareId);
        if (isMounted) {
          setSnapshot(serverData);
          setLoading(false);
        }
      } catch {
        // Fallback: check if it's a legacy un-prefixed client token
        try {
          const fallbackData = await decodeConversationSnapshot(shareId);
          if (isMounted) {
            setSnapshot(fallbackData);
            setLoading(false);
          }
        } catch {
          if (isMounted) {
            setSnapshot(null);
            setLoading(false);
          }
        }
      }
    }

    loadSharedSnapshot();

    return () => {
      isMounted = false;
    };
  }, [shareId]);

  async function handleCopyPageLink() {
    if (typeof window !== "undefined") {
      const success = await copyShareLink(window.location.href);
      if (success) {
        setLinkCopied(true);
        setTimeout(() => setLinkCopied(false), 2400);
      }
    }
  }

  return (
    <div className="min-h-screen bg-base text-ink-primary">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-40 border-b border-border-subtle bg-surface/90 backdrop-blur-md">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-3 sm:px-6">
          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="flex items-center gap-2 transition-opacity hover:opacity-85"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-teal/15 text-teal">
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <circle cx="6" cy="6" r="3" />
                  <circle cx="18" cy="6" r="3" />
                  <circle cx="12" cy="18" r="3" />
                  <line x1="8.5" y1="7.5" x2="10.5" y2="15.5" />
                  <line x1="15.5" y1="7.5" x2="13.5" y2="15.5" />
                </svg>
              </div>
              <span className="font-display text-[16px] font-bold tracking-tight text-ink-primary">
                EduGraph<span className="text-teal">AI</span>
              </span>
            </Link>

            <span className="hidden items-center gap-1.5 rounded-full border border-teal/30 bg-teal-dim/60 px-2.5 py-0.5 text-[11px] font-medium text-teal sm:inline-flex">
              <svg
                width="12"
                height="12"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <circle cx="12" cy="12" r="10" />
                <line x1="2" y1="12" x2="22" y2="12" />
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
              </svg>
              Shared Snapshot
            </span>
          </div>

          <div className="flex items-center gap-2.5">
            {snapshot && (
              <button
                onClick={handleCopyPageLink}
                className="btn-ghost hidden !px-3 !py-1.5 text-[12.5px] text-ink-secondary hover:text-ink-primary sm:inline-flex"
                title="Copy share link"
              >
                {linkCopied ? "✓ Link Copied" : "Copy Link"}
              </button>
            )}
            <Link
              href="/"
              className="btn-primary !px-3.5 !py-1.5 text-[13px] font-semibold"
            >
              Open EduGraphAI →
            </Link>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="mx-auto max-w-4xl px-4 py-8 sm:px-6">
        {loading ? (
          <div className="space-y-6 animate-pulse">
            <div className="space-y-3">
              <div className="h-7 w-2/3 rounded-md bg-elevated" />
              <div className="h-4 w-1/3 rounded-md bg-elevated/70" />
            </div>
            <div className="space-y-4 pt-4">
              <div className="h-24 rounded-lg border border-border-subtle bg-elevated/40" />
              <div className="h-48 rounded-lg border border-border-subtle bg-elevated/40" />
            </div>
          </div>
        ) : !snapshot ? (
          <div className="my-16 flex flex-col items-center justify-center text-center animate-fadein">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-amber-dim text-2xl text-amber">
              💬
            </div>
            <h1 className="mt-4 font-display text-xl font-bold text-ink-primary">
              This shared conversation is unavailable.
            </h1>
            <p className="mt-1.5 max-w-md text-[13.5px] text-ink-secondary">
              The link may be incomplete or corrupted. Ask the sender for a new link
              or start your own conversation.
            </p>
            <div className="mt-6">
              <Link href="/" className="btn-primary !px-5 !py-2 text-[13.5px]">
                Open EduGraphAI
              </Link>
            </div>
          </div>
        ) : (
          <div className="space-y-8 animate-fadein">
            {/* Header info */}
            <div className="border-b border-border-subtle pb-6">
              <div className="flex flex-wrap items-center gap-2.5 text-[11.5px] font-medium text-ink-tertiary">
                {snapshot.topic && (
                  <span className="rounded bg-teal-dim px-2.5 py-0.5 font-semibold text-teal">
                    {snapshot.topic}
                  </span>
                )}
                <span>
                  {snapshot.messages.length}{" "}
                  {snapshot.messages.length === 1 ? "turn" : "turns"}
                </span>
                <span>·</span>
                <span className="rounded border border-border-subtle bg-elevated px-2 py-0.5 text-[10.5px]">
                  Read-only snapshot
                </span>
              </div>

              <h1 className="mt-3 font-display text-2xl font-bold tracking-tight text-ink-primary sm:text-3xl">
                {snapshot.title}
              </h1>
            </div>

            {/* Conversation message stream */}
            <div className="space-y-6">
              {snapshot.messages.map((msg: SharedMessage, index: number) => {
                const isUser = msg.role === "user";

                if (isUser) {
                  return (
                    <div
                      key={`msg-${index}`}
                      className="flex items-start gap-3.5 rounded-xl border border-border-subtle bg-surface/80 p-4.5 sm:p-5"
                    >
                      <div
                        aria-hidden="true"
                        className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full border border-teal/40 bg-teal-dim text-xs font-bold text-teal"
                      >
                        Q
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="text-[11px] font-semibold uppercase tracking-wider text-teal">
                          Question
                        </div>
                        <p className="mt-1 font-medium text-[15px] leading-relaxed text-ink-primary">
                          {msg.content}
                        </p>
                      </div>
                    </div>
                  );
                }

                // Assistant response
                return (
                  <div
                    key={`msg-${index}`}
                    className="flex items-start gap-3.5 rounded-xl border border-border-subtle bg-elevated/30 p-4.5 sm:p-6 shadow-sm"
                  >
                    <div
                      aria-hidden="true"
                      className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full border border-violet/40 bg-violet-dim text-xs font-bold text-violet"
                    >
                      A
                    </div>
                    <div className="min-w-0 flex-1 space-y-2">
                      <div className="flex items-center justify-between text-[11px] font-semibold uppercase tracking-wider text-violet">
                        <span>EduGraphAI Response</span>
                        {msg.topic && (
                          <span className="lowercase font-mono text-[10.5px] text-ink-tertiary">
                            topic: {msg.topic}
                          </span>
                        )}
                      </div>
                      <div className="pt-1">{parseMarkdownBlocks(msg.content)}</div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Footer Call to Action */}
            <div className="mt-12 rounded-xl border border-border-subtle bg-elevated/60 p-6 text-center sm:p-8">
              <h2 className="font-display text-lg font-bold text-ink-primary">
                Explore Knowledge Graph-Powered Learning
              </h2>
              <p className="mx-auto mt-2 max-w-lg text-[13.5px] leading-relaxed text-ink-secondary">
                EduGraphAI maps conceptual relationships across academic domains,
                generating grounded, exam-ready answers and interactive knowledge
                graphs.
              </p>
              <div className="mt-5 flex items-center justify-center gap-3">
                <Link
                  href="/"
                  className="btn-primary !px-5 !py-2.5 text-[13.5px] font-semibold"
                >
                  Start Your Own Learning Session →
                </Link>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
