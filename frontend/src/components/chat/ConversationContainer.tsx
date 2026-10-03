"use client";

import { useMemo } from "react";
import { ChatMessage, Conversation } from "@/lib/types";
import ChatInput, { AVAILABLE_SUBJECTS } from "./ChatInput";
import ChatHistory from "./ChatHistory";

interface ConversationContainerProps {
  conversation: Conversation | null;
  isLoading: boolean;
  isSendBlocked?: boolean;
  onSubmitQuery: (query: string, subject?: string | null) => void;
  onStopGenerating?: () => void;
  selectedSubject: string | null;
  onSelectSubject: (subject: string | null) => void;
  initialQuery?: string;
  onClearInitialQuery?: () => void;
  onEditQuery?: (query: string) => void;
  onRetryAsk: (messageId: string, query: string) => void;
  onDismissAskError?: (messageId: string) => void;
  onRetryGraph: (messageId: string, query: string) => void;
  onRegenerate: (messageId: string, query: string) => void;
  onShareConversation?: () => void;
  onOpenGraphModal?: (message: ChatMessage) => void;
  bookmarkedTopics: string[];
  onToggleBookmark: (topic: string, answer: string) => void;
}

const SUBJECT_EXAMPLES: Record<string, string[]> = {
  DSA: [
    "Explain Binary Search for 8 marks",
    "Compare AVL Tree vs Red-Black Tree",
    "Explain recursion simply with an example",
    "How does Quick Sort partition work?",
  ],
  ADA: [
    "Explain Dijkstra's Algorithm for 10 marks",
    "Explain Dynamic Programming vs Greedy approach",
    "Give 5-mark answer for Fractional Knapsack",
    "What are asymptotic notations (Big-O, Omega, Theta)?",
  ],
  CN: [
    "Create revision notes for OSI Model 7 layers",
    "Explain TCP 3-Way Handshake for 8 marks",
    "Compare IPv4 vs IPv6 addressing",
    "How does DNS resolution work step-by-step?",
  ],
  ML: [
    "Explain Overfitting vs Underfitting simply",
    "Compare Supervised vs Unsupervised Learning",
    "Give 10-mark answer on Gradient Descent",
    "What is the Bias-Variance tradeoff?",
  ],
  OS: [
    "Explain Process Scheduling algorithms for 8 marks",
    "What are the 4 conditions for Deadlock?",
    "Compare Paging vs Segmentation in memory management",
    "Explain Virtual Memory and Demand Paging",
  ],
  SEPM: [
    "Compare Agile vs Waterfall model for 10 marks",
    "Explain Software Testing Life Cycle (STLC)",
    "What is Scrum framework and sprint lifecycle?",
    "Explain COCOMO model for software cost estimation",
  ],
};

const GENERAL_EXAMPLES = [
  "Explain Quick Sort for 8 marks",
  "Explain recursion simply",
  "Give a 10-mark answer for TCP/IP vs OSI",
  "Compare BFS and DFS with time complexity",
  "Show prerequisites for Machine Learning",
  "Explain Deadlock avoidance and Banker's Algorithm",
];

export default function ConversationContainer({
  conversation,
  isLoading,
  isSendBlocked = false,
  onSubmitQuery,
  onStopGenerating,
  selectedSubject,
  onSelectSubject,
  initialQuery,
  onClearInitialQuery,
  onEditQuery,
  onRetryAsk,
  onDismissAskError,
  onRetryGraph,
  onRegenerate,
  onShareConversation,
  onOpenGraphModal,
  bookmarkedTopics,
  onToggleBookmark,
}: ConversationContainerProps) {
  const hasMessages = !!conversation && conversation.messages.length > 0;
  const inputDisabled = isLoading || isSendBlocked;

  const currentPrompts = useMemo(() => {
    if (selectedSubject && SUBJECT_EXAMPLES[selectedSubject]) {
      return SUBJECT_EXAMPLES[selectedSubject];
    }
    return GENERAL_EXAMPLES;
  }, [selectedSubject]);

  if (!hasMessages) {
    return (
      <div className="flex h-[calc(100vh-60px)] flex-col overflow-y-auto">
        <div className="mx-auto flex flex-1 w-full max-w-[800px] flex-col items-center justify-center px-4 py-8 text-center sm:px-6">
          {/* Logo Mark */}
          <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl border border-teal/30 bg-teal-dim/30 shadow-[0_0_20px_rgba(69,214,198,0.15)]">
            <svg
              width="36"
              height="36"
              viewBox="0 0 30 30"
              fill="none"
              aria-hidden="true"
            >
              <line x1="7" y1="8" x2="15" y2="22" stroke="#45d6c6" strokeWidth="1.6" />
              <line x1="23" y1="8" x2="15" y2="22" stroke="#45d6c6" strokeWidth="1.6" />
              <line x1="7" y1="8" x2="23" y2="8" stroke="#343b4d" strokeWidth="1.6" />
              <circle cx="7" cy="8" r="3.4" fill="#1b1f2a" stroke="#8b7ff0" strokeWidth="1.6" />
              <circle cx="23" cy="8" r="3.4" fill="#1b1f2a" stroke="#8b7ff0" strokeWidth="1.6" />
              <circle cx="15" cy="22" r="4.2" fill="#45d6c6" />
            </svg>
          </div>

          {/* Heading */}
          <h2 className="mb-2 font-display text-2xl font-bold text-ink-primary sm:text-3xl">
            EduGraphAI — Knowledge-Graph Educational Assistant
          </h2>
          <p className="mb-6 max-w-[560px] text-[14px] leading-relaxed text-ink-secondary sm:text-[15px]">
            Every explanation is grounded in Neo4j educational knowledge graphs. Explore syllabus
            hierarchies, prerequisite chains, and get exam-ready answers.
          </p>

          {/* Subject Syllabus Filter Cards */}
          <div className="mb-5 grid w-full grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-6">
            {AVAILABLE_SUBJECTS.filter((s) => s.id !== null).map((sub) => {
              const isSelected = selectedSubject === sub.id;
              return (
                <button
                  key={sub.id}
                  onClick={() => onSelectSubject(isSelected ? null : sub.id)}
                  className={`flex flex-col items-center gap-1 rounded-xl border p-2.5 text-center transition-all hover:-translate-y-0.5 ${
                    isSelected
                      ? "border-teal bg-teal-dim/40 shadow-[0_0_12px_rgba(69,214,198,0.2)]"
                      : "border-border-subtle bg-elevated/60 hover:border-teal/50 hover:bg-elevated"
                  }`}
                >
                  <span className="text-xl">{sub.icon}</span>
                  <span className={`text-[12px] font-semibold ${isSelected ? "text-teal" : "text-ink-primary"}`}>
                    {sub.badge}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Hero Input Box */}
          <div className="w-full">
            <ChatInput
              onSubmit={onSubmitQuery}
              isLoading={inputDisabled}
              onStopGenerating={onStopGenerating}
              selectedSubject={selectedSubject}
              onSelectSubject={onSelectSubject}
              initialValue={initialQuery}
              onClearInitialValue={onClearInitialQuery}
              variant="hero"
            />
          </div>

          {/* Example prompt pills */}
          <div className="mt-4 flex flex-wrap justify-center gap-2">
            {currentPrompts.map((prompt) => (
              <button
                key={prompt}
                onClick={() => onSubmitQuery(prompt, selectedSubject)}
                className="rounded-full border border-border-subtle bg-elevated/70 px-3 py-1.5 text-[12px] text-ink-secondary transition-all hover:border-teal hover:bg-teal-dim/20 hover:text-ink-primary hover:-translate-y-0.5"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-60px)] flex-col">
      <ChatHistory
        conversation={conversation!}
        isLoading={isLoading}
        onSelectTopic={(q) => onSubmitQuery(q, selectedSubject)}
        onRetryAsk={onRetryAsk}
        onDismissAskError={onDismissAskError}
        onRetryGraph={onRetryGraph}
        onRegenerate={onRegenerate}
        onEditQuery={onEditQuery}
        onShareConversation={onShareConversation}
        onOpenGraphModal={onOpenGraphModal}
        bookmarkedTopics={bookmarkedTopics}
        onToggleBookmark={onToggleBookmark}
      />
      <div className="border-t border-border-subtle bg-base px-4 py-3 sm:px-6">
        <div className="mx-auto max-w-[920px]">
          <ChatInput
            onSubmit={onSubmitQuery}
            isLoading={inputDisabled}
            onStopGenerating={onStopGenerating}
            selectedSubject={selectedSubject}
            onSelectSubject={onSelectSubject}
            initialValue={initialQuery}
            onClearInitialValue={onClearInitialQuery}
          />
        </div>
      </div>
    </div>
  );
}
