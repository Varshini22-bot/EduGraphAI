"use client";

import { useState } from "react";
import { AnswerStyle, LearningLevel } from "@/lib/settingsStorage";

interface AnswerCardProps {
  topic: string;
  answer: string;
  answerStyle: AnswerStyle;
  learningLevel: LearningLevel;
}

// ---------------------------------------------------------------------------
// Lightweight markdown-lite rendering for the AI answer, plus PRESENTATION
// ONLY adjustments for answerStyle/learningLevel.
//
// HONESTY BOUNDARY (unchanged from before): RAGService.answer() returns one
// plain-text string, with no structured fields. This renders whatever
// markdown-like structure the LLM's text already contains (headings, lists,
// **bold**, fenced ```code``` blocks, | tables |) — it does not invent
// structure that isn't there.
//
// NOTE on "syntax highlighting": this renders code blocks as clean,
// monospaced, copyable blocks with language labels — it does NOT do real
// token-level syntax highlighting (keywords/strings/etc. in color), since
// that would require a library (e.g. Prism/highlight.js) that isn't
// installed and couldn't be verified installing in this environment. Flagged
// honestly here and in the delivery report rather than faked.
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
      // clipboard denied — silently ignore, copy button just won't confirm
    }
  }

  return (
    <div className="overflow-hidden rounded-lg border border-border-subtle bg-base">
      <div className="flex items-center justify-between border-b border-border-subtle bg-elevated px-3 py-1.5">
        <span className="font-mono text-[11px] text-ink-tertiary">{language || "code"}</span>
        <button
          onClick={handleCopy}
          className="text-[11px] text-ink-tertiary hover:text-ink-primary"
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
    <div className="overflow-x-auto rounded-lg border border-border-subtle">
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
                <td key={ci} className="border-t border-border-subtle px-3 py-2 text-ink-primary/90">
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

function parseBlocks(answer: string): JSX.Element[] {
  const lines = answer.split("\n");
  const blocks: JSX.Element[] = [];
  let bulletBuffer: string[] = [];
  let numberedBuffer: string[] = [];

  function flushBullets(keyBase: string) {
    if (bulletBuffer.length === 0) return;
    blocks.push(
      <ul key={`ul-${keyBase}`} className="list-disc space-y-1 pl-5">
        {bulletBuffer.map((item, i) => (
          <li key={i} className="text-[14.5px] leading-[1.7] text-ink-primary/90">
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
      <ol key={`ol-${keyBase}`} className="list-decimal space-y-1 pl-5">
        {numberedBuffer.map((item, i) => (
          <li key={i} className="text-[14.5px] leading-[1.7] text-ink-primary/90">
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

    // Fenced code block: ```language ... ```
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
        <CodeBlock key={`code-${i}`} code={codeLines.join("\n")} language={language} />
      );
      continue;
    }

    // Markdown table: a row starting/ending with |, followed by a divider row
    if (isTableRow(line) && i + 1 < lines.length && isTableDivider(lines[i + 1])) {
      flushBullets(String(i));
      flushNumbered(String(i));
      const headers = splitTableRow(line);
      const rows: string[][] = [];
      i += 2; // skip header + divider
      while (i < lines.length && isTableRow(lines[i])) {
        rows.push(splitTableRow(lines[i]));
        i++;
      }
      blocks.push(<Table key={`table-${i}`} headers={headers} rows={rows} />);
      continue;
    }

    const headingMatch = line.match(/^#{2,4}\s+(.*)$/);
    if (headingMatch) {
      flushBullets(String(i));
      flushNumbered(String(i));
      blocks.push(
        <h3 key={`h-${i}`} className="mt-1 text-[14px] font-semibold text-ink-primary">
          {renderInline(headingMatch[1], `h-${i}`)}
        </h3>
      );
      i++;
      continue;
    }

    const bulletMatch = line.match(/^[-•]\s+(.*)$/);
    if (bulletMatch) {
      flushNumbered(String(i));
      bulletBuffer.push(bulletMatch[1]);
      i++;
      continue;
    }

    const numberedMatch = line.match(/^\d+[.)]\s+(.*)$/);
    if (numberedMatch) {
      flushBullets(String(i));
      numberedBuffer.push(numberedMatch[1]);
      i++;
      continue;
    }

    flushBullets(String(i));
    flushNumbered(String(i));
    blocks.push(
      <p key={`p-${i}`} className="text-[14.5px] leading-[1.75] text-ink-primary/90">
        {renderInline(line, `p-${i}`)}
      </p>
    );
    i++;
  }

  flushBullets("end");
  flushNumbered("end");

  return blocks;
}

const LEVEL_LABEL: Record<LearningLevel, string> = {
  beginner: "Beginner",
  intermediate: "Intermediate",
  advanced: "Advanced",
};

export default function AnswerCard({
  topic,
  answer,
  answerStyle,
  learningLevel,
}: AnswerCardProps) {
  const blocks = parseBlocks(answer);
  const visibleBlocks = answerStyle === "simple" ? blocks.slice(0, 1) : blocks;
  const isExamFriendly = answerStyle === "exam-friendly";

  return (
    <div className="animate-fadein" aria-label="AI answer">
      <div className="mb-2 flex flex-wrap items-center gap-2">
        <h2 className="font-display text-[19px] font-bold text-ink-primary">{topic}</h2>
        <span className="rounded-full bg-violet-dim px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-violet">
          {LEVEL_LABEL[learningLevel]}
        </span>
        {isExamFriendly && (
          <span className="rounded-full bg-amber-dim px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-amber">
            Exam-friendly
          </span>
        )}
      </div>

      <div
        className={
          isExamFriendly
            ? "flex flex-col gap-2.5 border-l-2 border-amber/50 pl-3.5"
            : "flex flex-col gap-2.5"
        }
      >
        {visibleBlocks}
      </div>

      {answerStyle === "simple" && blocks.length > 1 && (
        <p className="mt-2 text-[11.5px] italic text-ink-tertiary">
          Simplified view — switch to Detailed in Settings to see the full explanation.
        </p>
      )}
    </div>
  );
}
