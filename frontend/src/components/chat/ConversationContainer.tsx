import { Conversation } from "@/lib/types";
import ChatInput from "./ChatInput";
import ChatHistory from "./ChatHistory";

interface ConversationContainerProps {
  conversation: Conversation | null;
  isLoading: boolean;
  onSubmitQuery: (query: string) => void;
  onRetryAsk: (messageId: string, query: string) => void;
  onRetryGraph: (messageId: string, query: string) => void;
  onRegenerate: (messageId: string, query: string) => void;
  bookmarkedTopics: string[];
  onToggleBookmark: (topic: string, answer: string) => void;
}

// Text-only examples — clicking one submits it as a normal question.
const EXAMPLE_PROMPTS = [
  "Explain Binary Search for 8 marks",
  "Explain recursion simply",
  "Give a 10-mark answer for DBMS normalization",
  "Compare BFS and DFS",
  "Show prerequisites for Machine Learning",
  "Create revision notes for OSI model",
];

export default function ConversationContainer({
  conversation,
  isLoading,
  onSubmitQuery,
  onRetryAsk,
  onRetryGraph,
  onRegenerate,
  bookmarkedTopics,
  onToggleBookmark,
}: ConversationContainerProps) {
  const hasMessages = !!conversation && conversation.messages.length > 0;

  if (!hasMessages) {
    return (
      <div className="flex h-[calc(100vh-60px)] flex-col">
        <div className="flex flex-1 flex-col items-center justify-center px-6 text-center">
          <svg
            width="52"
            height="52"
            viewBox="0 0 30 30"
            fill="none"
            aria-hidden="true"
            className="mb-4.5 opacity-90"
          >
            <line x1="7" y1="8" x2="15" y2="22" stroke="#45d6c6" strokeWidth="1" />
            <line x1="23" y1="8" x2="15" y2="22" stroke="#45d6c6" strokeWidth="1" />
            <line x1="7" y1="8" x2="23" y2="8" stroke="#343b4d" strokeWidth="1" />
            <circle cx="7" cy="8" r="3.4" fill="#1b1f2a" stroke="#8b7ff0" strokeWidth="1.4" />
            <circle cx="23" cy="8" r="3.4" fill="#1b1f2a" stroke="#8b7ff0" strokeWidth="1.4" />
            <circle cx="15" cy="22" r="4" fill="#45d6c6" />
          </svg>
          <h2 className="mb-2 max-w-[520px] font-display text-2xl font-bold text-ink-primary sm:text-[28px]">
            Ask anything. See how it connects.
          </h2>
          <p className="mb-7 max-w-[480px] text-[14.5px] leading-relaxed text-ink-secondary">
            The Knowledge Graph Learning Assistant explains any topic, then
            shows you exactly how it links to everything else you should
            learn next.
          </p>
          <div className="w-full max-w-[640px]">
            <ChatInput onSubmit={onSubmitQuery} isLoading={isLoading} variant="hero" />
          </div>
          <div className="mt-4.5 flex max-w-[640px] flex-wrap justify-center gap-2">
            {EXAMPLE_PROMPTS.map((prompt) => (
              <button
                key={prompt}
                onClick={() => onSubmitQuery(prompt)}
                className="rounded-full border border-border-subtle bg-elevated px-3.5 py-1.5 text-[12.5px] text-ink-secondary transition-colors hover:border-teal hover:text-ink-primary"
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
        onSelectTopic={onSubmitQuery}
        onRetryAsk={onRetryAsk}
        onRetryGraph={onRetryGraph}
        onRegenerate={onRegenerate}
        bookmarkedTopics={bookmarkedTopics}
        onToggleBookmark={onToggleBookmark}
      />
      <div className="border-t border-border-subtle bg-base px-4 py-4 sm:px-6">
        <div className="mx-auto max-w-[920px]">
          <ChatInput onSubmit={onSubmitQuery} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}
