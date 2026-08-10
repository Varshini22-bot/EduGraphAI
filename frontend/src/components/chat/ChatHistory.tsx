"use client";

import { useEffect, useRef } from "react";
import { Conversation } from "@/lib/types";
import ChatMessage from "./ChatMessage";

interface ChatHistoryProps {
  conversation: Conversation;
  isLoading: boolean;
  onSelectTopic: (topic: string) => void;
  onRetryAsk: (messageId: string, query: string) => void;
  onRetryGraph: (messageId: string, query: string) => void;
  onRegenerate: (messageId: string, query: string) => void;
  bookmarkedTopics: string[];
  onToggleBookmark: (topic: string, answer: string) => void;
}

export default function ChatHistory({
  conversation,
  isLoading,
  onSelectTopic,
  onRetryAsk,
  onRetryGraph,
  onRegenerate,
  bookmarkedTopics,
  onToggleBookmark,
}: ChatHistoryProps) {
  const endRef = useRef<HTMLDivElement>(null);

  // Defensive: guarantees bookmarkedTopics.includes(...) can never throw,
  // regardless of what the parent ever passes. The real fix is still that
  // page.tsx/ConversationContainer always supply a real array (traced and
  // confirmed below) — this is a belt-and-suspenders guard, not a
  // replacement for that.
  const safeBookmarkedTopics = Array.isArray(bookmarkedTopics) ? bookmarkedTopics : [];

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversation.messages.length, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto px-4 pb-3 pt-6 sm:px-6">
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
            onRetryGraph={onRetryGraph}
            onRegenerate={onRegenerate}
            isBookmarked={
              !!message.response && safeBookmarkedTopics.includes(message.response.topic)
            }
            onToggleBookmark={onToggleBookmark}
          />
        ))}
        <div ref={endRef} />
      </div>
    </div>
  );
}
