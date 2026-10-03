"use client";

import { useEffect, useRef, useState } from "react";
import { ChatMessage as ChatMessageType, Conversation } from "@/lib/types";
import ChatMessage from "./ChatMessage";

interface ChatHistoryProps {
  conversation: Conversation;
  isLoading: boolean;
  onSelectTopic: (topic: string) => void;
  onRetryAsk: (messageId: string, query: string) => void;
  onDismissAskError?: (messageId: string) => void;
  onRetryGraph: (messageId: string, query: string) => void;
  onRegenerate: (messageId: string, query: string) => void;
  onEditQuery?: (query: string) => void;
  onShareConversation?: () => void;
  onOpenGraphModal?: (message: ChatMessageType) => void;
  bookmarkedTopics: string[];
  onToggleBookmark: (topic: string, answer: string) => void;
}

export default function ChatHistory({
  conversation,
  isLoading,
  onSelectTopic,
  onRetryAsk,
  onDismissAskError,
  onRetryGraph,
  onRegenerate,
  onEditQuery,
  onShareConversation,
  onOpenGraphModal,
  bookmarkedTopics,
  onToggleBookmark,
}: ChatHistoryProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const [isAtBottom, setIsAtBottom] = useState(true);
  const [showScrollBottom, setShowScrollBottom] = useState(false);
  const prevMessageCountRef = useRef(conversation.messages.length);

  const safeBookmarkedTopics = Array.isArray(bookmarkedTopics) ? bookmarkedTopics : [];

  function scrollToBottom(smooth = true) {
    if (endRef.current) {
      endRef.current.scrollIntoView({ behavior: smooth ? "smooth" : "auto" });
      setIsAtBottom(true);
      setShowScrollBottom(false);
    }
  }

  function handleScroll() {
    const el = containerRef.current;
    if (!el) return;
    const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
    const atBottom = distanceFromBottom < 100;
    setIsAtBottom(atBottom);
    setShowScrollBottom(!atBottom);
  }

  // Auto-scroll logic: only jump down automatically if the user is already near
  // the bottom, or if a brand new message was appended.
  useEffect(() => {
    const messageCount = conversation.messages.length;
    const isNewMessage = messageCount > prevMessageCountRef.current;
    prevMessageCountRef.current = messageCount;

    if (isNewMessage || isAtBottom) {
      scrollToBottom(true);
    }
  }, [conversation.messages.length, isLoading, isAtBottom]);

  return (
    <div
      ref={containerRef}
      onScroll={handleScroll}
      className="relative flex-1 overflow-y-auto px-4 pb-4 pt-6 sm:px-6"
    >
      <div className="chat-thread-gap mx-auto flex max-w-[920px] flex-col gap-7">
        {conversation.messages.map((message, index) => (
          <ChatMessage
            key={message.id}
            message={message}
            isAskPending={
              isLoading &&
              index === conversation.messages.length - 1 &&
              !message.response &&
              !message.askError
            }
            onSelectTopic={onSelectTopic}
            onRetryAsk={onRetryAsk}
            onDismissAskError={onDismissAskError}
            onRetryGraph={onRetryGraph}
            onRegenerate={onRegenerate}
            onEditQuery={onEditQuery}
            onShareConversation={onShareConversation}
            onOpenGraphModal={onOpenGraphModal}
            isBookmarked={
              !!message.response && safeBookmarkedTopics.includes(message.response.topic)
            }
            onToggleBookmark={onToggleBookmark}
          />
        ))}
        <div ref={endRef} />
      </div>

      {/* Floating Scroll to Bottom button (Phase 1, Item 8) */}
      {showScrollBottom && (
        <button
          type="button"
          onClick={() => scrollToBottom(true)}
          className="fixed bottom-24 right-6 z-20 flex h-9 w-9 items-center justify-center rounded-full border border-border-subtle bg-elevated text-ink-primary shadow-elevated transition-transform hover:scale-110 active:scale-95 sm:right-10"
          title="Scroll to newest message"
          aria-label="Scroll to bottom"
        >
          <span className="font-bold text-sm">↓</span>
        </button>
      )}
    </div>
  );
}
